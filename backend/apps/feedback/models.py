import secrets

from django.db import models

from apps.catalog.models import DomainPromptVersion, Question
from apps.core.models import TimeStampedModel
from apps.locations.models import Location


def session_token() -> str:
    return secrets.token_urlsafe(32)


class FeedbackSession(TimeStampedModel):
    class Status(models.TextChoices):
        STARTED = "started", "Started"
        SUBMITTED = "submitted", "Feedback submitted"
        GENERATED = "generated", "Drafts generated"
        COMPLETED = "completed", "Google opened"
        ABANDONED = "abandoned", "Abandoned"

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="feedback_sessions")
    anonymous_session_token = models.CharField(
        max_length=80, unique=True, default=session_token, editable=False
    )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    overall_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    optional_comment = models.TextField(blank=True)
    selected_draft = models.ForeignKey(
        "GeneratedDraft",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="selected_by_sessions",
    )
    final_review_text = models.TextField(blank=True)
    google_opened_at = models.DateTimeField(null=True, blank=True)
    generation_count = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.STARTED)
    language = models.CharField(max_length=10, default="en")
    feedback_idempotency_key = models.CharField(max_length=80, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["location", "created_at"]),
            models.Index(fields=["anonymous_session_token"]),
        ]

    def __str__(self) -> str:
        return f"{self.location.name} {self.anonymous_session_token[:8]}"


class FeedbackAnswer(TimeStampedModel):
    session = models.ForeignKey(FeedbackSession, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="answers")
    rating = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "question"], name="unique_session_question")
        ]


class GeneratedDraft(TimeStampedModel):
    class Style(models.TextChoices):
        SHORT = "short", "Short"
        NATURAL = "natural", "Natural"
        DETAILED = "detailed", "Detailed"

    session = models.ForeignKey(FeedbackSession, on_delete=models.CASCADE, related_name="drafts")
    style = models.CharField(max_length=20, choices=Style.choices)
    text = models.TextField()
    prompt_version = models.ForeignKey(
        DomainPromptVersion, on_delete=models.PROTECT, related_name="generated_drafts"
    )
    model_identifier = models.CharField(max_length=180)
    generation_duration_ms = models.PositiveIntegerField(default=0)
    generation_attempt = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "style", "generation_attempt"],
                name="unique_session_style_attempt",
            )
        ]


class AnalyticsEvent(TimeStampedModel):
    class EventType(models.TextChoices):
        QR_SCANNED = "qr_scanned", "QR scanned"
        FORM_STARTED = "form_started", "Form started"
        FEEDBACK_SUBMITTED = "feedback_submitted", "Feedback submitted"
        GENERATION_REQUESTED = "generation_requested", "Generation requested"
        GENERATION_SUCCEEDED = "generation_succeeded", "Generation succeeded"
        GENERATION_FAILED = "generation_failed", "Generation failed"
        DRAFT_SELECTED = "draft_selected", "Draft selected"
        DRAFT_EDITED = "draft_edited", "Draft edited"
        COPY_SUCCEEDED = "copy_succeeded", "Copy succeeded"
        COPY_FAILED = "copy_failed", "Copy failed"
        GOOGLE_OPEN_CLICKED = "google_open_clicked", "Google opened"

    session = models.ForeignKey(FeedbackSession, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    idempotency_key = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["session", "event_type", "created_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "event_type", "idempotency_key"],
                condition=~models.Q(idempotency_key=""),
                name="unique_idempotent_event",
            )
        ]
