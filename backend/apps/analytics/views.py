from datetime import timedelta

from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.feedback.models import AnalyticsEvent, FeedbackAnswer, FeedbackSession
from apps.locations.models import Location
from apps.locations.permissions import IsApprovedMerchant

from .serializers import MerchantFeedbackListSerializer


def _period_days(value: str | None) -> int:
    try:
        days = int(value or 30)
    except ValueError:
        return 30
    return days if days in {7, 30, 90} else 30


class MerchantLocationMixin:
    permission_classes = [IsApprovedMerchant]

    def get_location(self):
        return Location.objects.filter(merchant_account=self.request.user.merchant_account).first()


class OverviewView(MerchantLocationMixin, APIView):
    def get(self, request):
        location = self.get_location()
        if not location:
            return Response({"detail": "Create a location first."}, status=409)
        days = _period_days(request.query_params.get("period"))
        now = timezone.now()
        start = now - timedelta(days=days)
        previous_start = start - timedelta(days=days)

        sessions = FeedbackSession.objects.filter(location=location, created_at__gte=start)
        previous_sessions = FeedbackSession.objects.filter(
            location=location, created_at__gte=previous_start, created_at__lt=start
        )
        events = AnalyticsEvent.objects.filter(session__location=location, created_at__gte=start)

        event_counts = {
            row["event_type"]: row["count"]
            for row in events.values("event_type").annotate(count=Count("id"))
        }
        scans = event_counts.get(AnalyticsEvent.EventType.QR_SCANNED, 0)
        completed = event_counts.get(AnalyticsEvent.EventType.FEEDBACK_SUBMITTED, 0)
        generations = event_counts.get(AnalyticsEvent.EventType.GENERATION_SUCCEEDED, 0)
        selections = event_counts.get(AnalyticsEvent.EventType.DRAFT_SELECTED, 0)
        google_opens = event_counts.get(AnalyticsEvent.EventType.GOOGLE_OPEN_CLICKED, 0)

        overall = sessions.exclude(overall_rating=None).aggregate(value=Avg("overall_rating"))["value"]
        previous_overall = previous_sessions.exclude(overall_rating=None).aggregate(
            value=Avg("overall_rating")
        )["value"]

        trend = list(
            sessions.exclude(overall_rating=None)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(average=Avg("overall_rating"), responses=Count("id"))
            .order_by("day")
        )
        for item in trend:
            item["day"] = item["day"].isoformat()
            item["average"] = round(float(item["average"]), 2)

        aspects = list(
            FeedbackAnswer.objects.filter(session__location=location, session__created_at__gte=start)
            .values("question__aspect_id", "question__display_label")
            .annotate(average=Avg("rating"), responses=Count("id"))
            .order_by("question__order")
        )
        normalized_aspects = [
            {
                "aspect_id": row["question__aspect_id"],
                "label": row["question__display_label"],
                "average": round(float(row["average"]), 2),
                "responses": row["responses"],
            }
            for row in aspects
        ]

        highlights: list[dict[str, str]] = []
        response_count = sessions.filter(submitted_at__isnull=False).count()
        if response_count < 5:
            highlights.append({"type": "insufficient-data", "text": "Not enough feedback to show a reliable comparison yet."})
        elif normalized_aspects:
            highest = max(normalized_aspects, key=lambda row: row["average"])
            lowest = min(normalized_aspects, key=lambda row: row["average"])
            highlights.extend(
                [
                    {"type": "highest", "text": f"{highest['label']} was highest at {highest['average']}/5."},
                    {"type": "lowest", "text": f"{lowest['label']} was lowest at {lowest['average']}/5."},
                ]
            )
            if overall is not None and previous_overall is not None:
                change = round(float(overall - previous_overall), 2)
                if abs(change) >= 0.2:
                    direction = "increased" if change > 0 else "decreased"
                    highlights.append(
                        {"type": "change", "text": f"Overall experience {direction} by {abs(change)} versus the previous period."}
                    )

        def rate(numerator: int, denominator: int) -> float | None:
            return round(numerator / denominator * 100, 1) if denominator else None

        return Response(
            {
                "period_days": days,
                "response_count": response_count,
                "metrics": {
                    "qr_scans": scans,
                    "feedback_completed": completed,
                    "generation_succeeded": generations,
                    "draft_selections": selections,
                    "google_page_opened": google_opens,
                    "feedback_completion_rate": rate(completed, scans),
                    "google_open_rate": rate(google_opens, completed),
                    "average_overall_score": round(float(overall), 2) if overall is not None else None,
                },
                "trend": trend,
                "aspects": normalized_aspects,
                "highlights": highlights,
            }
        )


class FeedbackListView(MerchantLocationMixin, ListAPIView):
    serializer_class = MerchantFeedbackListSerializer

    def get_queryset(self):
        location = self.get_location()
        if not location:
            return FeedbackSession.objects.none()
        days = _period_days(self.request.query_params.get("period"))
        qs = (
            FeedbackSession.objects.filter(
                location=location,
                submitted_at__isnull=False,
                created_at__gte=timezone.now() - timedelta(days=days),
            )
            .select_related("selected_draft")
            .prefetch_related("answers__question")
            .order_by("-created_at")
        )
        classification = self.request.query_params.get("classification")
        if classification == "high-rated":
            qs = qs.filter(overall_rating__gte=4)
        elif classification == "neutral":
            qs = qs.filter(overall_rating=3)
        elif classification == "low-rated":
            qs = qs.filter(overall_rating__lte=2)
        return qs


class FeedbackDetailView(MerchantLocationMixin, RetrieveAPIView):
    serializer_class = MerchantFeedbackListSerializer
    lookup_url_kwarg = "feedback_id"

    def get_queryset(self):
        location = self.get_location()
        if not location:
            return FeedbackSession.objects.none()
        return (
            FeedbackSession.objects.filter(location=location)
            .select_related("selected_draft")
            .prefetch_related("answers__question", "drafts")
        )
