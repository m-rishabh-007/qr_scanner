from django.conf import settings
from rest_framework import serializers

from apps.catalog.models import Question

from .models import FeedbackSession, GeneratedDraft


class QuestionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "aspect_id",
            "display_label",
            "description",
            "order",
            "required",
            "minimum_rating",
            "maximum_rating",
        ]


class FeedbackAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)


class FeedbackSubmitSerializer(serializers.Serializer):
    answers = FeedbackAnswerInputSerializer(many=True)
    optional_comment = serializers.CharField(
        required=False, allow_blank=True, max_length=settings.MAX_COMMENT_LENGTH
    )
    idempotency_key = serializers.CharField(max_length=80)

    def validate(self, attrs):
        session: FeedbackSession = self.context["session"]
        active_questions = list(session.location.domain.questions.filter(active=True))
        active_by_id = {q.id: q for q in active_questions}
        received: dict[int, int] = {}
        for item in attrs["answers"]:
            question = active_by_id.get(item["question_id"])
            if not question:
                raise serializers.ValidationError("Question does not belong to this questionnaire.")
            rating = item["rating"]
            if not question.minimum_rating <= rating <= question.maximum_rating:
                raise serializers.ValidationError("Rating is outside the allowed range.")
            received[question.id] = rating
        missing = [q.display_label for q in active_questions if q.required and q.id not in received]
        if missing:
            raise serializers.ValidationError({"answers": f"Missing required ratings: {', '.join(missing)}"})
        attrs["normalized_answers"] = received
        return attrs


class GeneratedDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedDraft
        fields = ["id", "style", "text"]


class DraftSelectionSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=False)
    final_text = serializers.CharField(max_length=settings.MAX_REVIEW_LENGTH)

    def validate(self, attrs):
        session: FeedbackSession = self.context["session"]
        draft_id = attrs.get("draft_id")
        if draft_id and not session.drafts.filter(id=draft_id).exists():
            raise serializers.ValidationError("Draft does not belong to this session.")
        return attrs


class PublicEventSerializer(serializers.Serializer):
    event_type = serializers.ChoiceField(
        choices=["draft_edited", "copy_succeeded", "copy_failed", "google_open_clicked"]
    )
    idempotency_key = serializers.CharField(max_length=100)
    metadata = serializers.JSONField(required=False)
