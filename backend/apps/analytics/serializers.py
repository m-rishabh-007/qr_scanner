from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.feedback.models import FeedbackSession


class FeedbackAnswerSummarySerializer(serializers.Serializer):
    aspect_id = serializers.CharField()
    label = serializers.CharField()
    rating = serializers.IntegerField()


class MerchantFeedbackListSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    selected_draft_style = serializers.CharField(source="selected_draft.style", allow_null=True)
    google_opened = serializers.SerializerMethodField()
    classification = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackSession
        fields = [
            "id",
            "created_at",
            "submitted_at",
            "overall_rating",
            "optional_comment",
            "answers",
            "selected_draft_style",
            "final_review_text",
            "google_opened",
            "classification",
            "language",
        ]

    @extend_schema_field(FeedbackAnswerSummarySerializer(many=True))
    def get_answers(self, obj) -> list[dict[str, str | int]]:
        return [
            {
                "aspect_id": answer.question.aspect_id,
                "label": answer.question.display_label,
                "rating": answer.rating,
            }
            for answer in obj.answers.all()
        ]

    def get_google_opened(self, obj) -> bool:
        return bool(obj.google_opened_at)

    def get_classification(self, obj) -> str:
        if obj.overall_rating is None:
            return "unrated"
        if obj.overall_rating >= 4:
            return "high-rated"
        if obj.overall_rating == 3:
            return "neutral"
        return "low-rated"
