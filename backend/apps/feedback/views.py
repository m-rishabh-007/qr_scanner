from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.generation.exceptions import GenerationError
from apps.generation.service import ReviewGenerationService
from apps.locations.models import Location
from .models import AnalyticsEvent, FeedbackAnswer, FeedbackSession, GeneratedDraft
from .serializers import (
    DraftSelectionSerializer,
    FeedbackSubmitSerializer,
    GeneratedDraftSerializer,
    PublicEventSerializer,
    QuestionPublicSerializer,
)
from .services import record_event
from .throttles import GenerationThrottle


class PublicBaseView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]


class QuestionnaireConfigView(PublicBaseView):
    def get(self, request, qr_token):
        location = get_object_or_404(
            Location.objects.select_related("domain"), public_qr_token=qr_token, active=True
        )
        questions = location.domain.questions.filter(active=True).order_by("order")
        requested_language = request.query_params.get("language") or location.default_language
        if requested_language not in location.domain.supported_languages:
            requested_language = location.default_language
        translations = {}
        for question in questions.prefetch_related("translations"):
            match = next(
                (item for item in question.translations.all() if item.language_code == requested_language),
                None,
            )
            if match:
                translations[question.id] = match
        question_rows = []
        for question in questions:
            translation = translations.get(question.id)
            row = QuestionPublicSerializer(question).data
            if translation:
                row["display_label"] = translation.display_label
                row["description"] = translation.description
            question_rows.append(row)
        return Response(
            {
                "location": {
                    "name": location.name,
                    "logo_url": location.logo_url,
                    "domain": location.domain.slug,
                    "language": requested_language,
                    "supported_languages": location.domain.supported_languages,
                },
                "questions": question_rows,
            }
        )


class SessionCreateView(PublicBaseView):
    def post(self, request, qr_token):
        location = get_object_or_404(Location, public_qr_token=qr_token, active=True)
        language = request.data.get("language") or location.default_language
        if language not in location.domain.supported_languages:
            language = location.default_language
        session = FeedbackSession.objects.create(location=location, language=language)
        record_event(session, AnalyticsEvent.EventType.QR_SCANNED, idempotency_key="initial")
        record_event(session, AnalyticsEvent.EventType.FORM_STARTED, idempotency_key="initial")
        return Response({"session_token": session.anonymous_session_token}, status=201)


class FeedbackSubmitView(PublicBaseView):
    @transaction.atomic
    def post(self, request, session_token):
        session = get_object_or_404(
            FeedbackSession.objects.select_for_update().select_related("location__domain"),
            anonymous_session_token=session_token,
        )
        serializer = FeedbackSubmitSerializer(data=request.data, context={"session": session})
        serializer.is_valid(raise_exception=True)
        key = serializer.validated_data["idempotency_key"]
        if session.feedback_idempotency_key == key and session.submitted_at:
            return Response({"detail": "Feedback already recorded."})
        if session.submitted_at and session.feedback_idempotency_key != key:
            return Response({"detail": "Feedback has already been submitted."}, status=409)

        answers = serializer.validated_data["normalized_answers"]
        questions = {
            q.id: q for q in session.location.domain.questions.filter(id__in=answers.keys())
        }
        for question_id, rating in answers.items():
            FeedbackAnswer.objects.update_or_create(
                session=session, question=questions[question_id], defaults={"rating": rating}
            )
        overall_question = session.location.domain.questions.filter(
            aspect_id="overall_experience", active=True
        ).first()
        session.overall_rating = answers.get(overall_question.id) if overall_question else None
        session.optional_comment = serializer.validated_data.get("optional_comment", "").strip()
        session.submitted_at = timezone.now()
        session.status = FeedbackSession.Status.SUBMITTED
        session.feedback_idempotency_key = key
        session.save(
            update_fields=[
                "overall_rating",
                "optional_comment",
                "submitted_at",
                "status",
                "feedback_idempotency_key",
                "updated_at",
            ]
        )
        record_event(
            session,
            AnalyticsEvent.EventType.FEEDBACK_SUBMITTED,
            idempotency_key=key,
        )
        return Response({"detail": "Feedback recorded."})


class GenerateDraftsView(PublicBaseView):
    throttle_classes = [GenerationThrottle]

    def post(self, request, session_token):
        from django.conf import settings

        # Keep the database lock short; never hold it while waiting on the model server.
        with transaction.atomic():
            session = get_object_or_404(
                FeedbackSession.objects.select_for_update().select_related("location__domain"),
                anonymous_session_token=session_token,
            )
            if not session.submitted_at:
                return Response({"detail": "Submit feedback before generating drafts."}, status=409)
            if session.generation_count >= settings.MAX_GENERATIONS_PER_SESSION:
                return Response({"detail": "Generation limit reached."}, status=429)
            session.generation_count += 1
            session.save(update_fields=["generation_count", "updated_at"])
            generation_attempt = session.generation_count
            attempt_key = str(generation_attempt)
            record_event(
                session,
                AnalyticsEvent.EventType.GENERATION_REQUESTED,
                idempotency_key=attempt_key,
            )

        session = FeedbackSession.objects.select_related("location__domain").get(pk=session.pk)
        try:
            result, prompt, retry_attempt = ReviewGenerationService().generate(session)
        except GenerationError:
            record_event(
                session,
                AnalyticsEvent.EventType.GENERATION_FAILED,
                idempotency_key=attempt_key,
            )
            return Response(
                {
                    "fallback_required": True,
                    "detail": "Suggestions are temporarily unavailable. Write or paste your own review.",
                },
                status=503,
            )

        with transaction.atomic():
            locked = FeedbackSession.objects.select_for_update().get(pk=session.pk)
            created = [
                GeneratedDraft.objects.create(
                    session=locked,
                    style=draft.style,
                    text=draft.text,
                    prompt_version=prompt,
                    model_identifier=result.model_identifier,
                    generation_duration_ms=result.duration_ms,
                    generation_attempt=generation_attempt,
                )
                for draft in result.drafts
            ]
            locked.status = FeedbackSession.Status.GENERATED
            locked.save(update_fields=["status", "updated_at"])
            record_event(
                locked,
                AnalyticsEvent.EventType.GENERATION_SUCCEEDED,
                idempotency_key=attempt_key,
                metadata={"retry_attempt": retry_attempt, "duration_ms": result.duration_ms},
            )
        return Response({"drafts": GeneratedDraftSerializer(created, many=True).data})


class DraftSelectionView(PublicBaseView):
    @transaction.atomic
    def post(self, request, session_token):
        session = get_object_or_404(
            FeedbackSession.objects.select_for_update(), anonymous_session_token=session_token
        )
        serializer = DraftSelectionSerializer(data=request.data, context={"session": session})
        serializer.is_valid(raise_exception=True)
        draft_id = serializer.validated_data.get("draft_id")
        session.selected_draft = session.drafts.filter(id=draft_id).first() if draft_id else None
        session.final_review_text = serializer.validated_data["final_text"].strip()
        session.save(update_fields=["selected_draft", "final_review_text", "updated_at"])
        record_event(
            session,
            AnalyticsEvent.EventType.DRAFT_SELECTED,
            idempotency_key=str(draft_id or "manual"),
        )
        return Response({"detail": "Final text saved."})


class PublicEventView(PublicBaseView):
    @transaction.atomic
    def post(self, request, session_token):
        session = get_object_or_404(
            FeedbackSession.objects.select_for_update(), anonymous_session_token=session_token
        )
        serializer = PublicEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_type = serializer.validated_data["event_type"]
        record_event(
            session,
            event_type,
            idempotency_key=serializer.validated_data["idempotency_key"],
            metadata=serializer.validated_data.get("metadata", {}),
        )
        if event_type == AnalyticsEvent.EventType.GOOGLE_OPEN_CLICKED:
            session.google_opened_at = timezone.now()
            session.status = FeedbackSession.Status.COMPLETED
            session.save(update_fields=["google_opened_at", "status", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
