from django.contrib import admin

from .models import AnalyticsEvent, FeedbackAnswer, FeedbackSession, GeneratedDraft


class AnswerInline(admin.TabularInline):
    model = FeedbackAnswer
    extra = 0
    readonly_fields = ("question", "rating", "created_at")


class DraftInline(admin.TabularInline):
    model = GeneratedDraft
    extra = 0
    readonly_fields = ("style", "text", "prompt_version", "model_identifier", "created_at")


@admin.register(FeedbackSession)
class FeedbackSessionAdmin(admin.ModelAdmin):
    list_display = ("location", "overall_rating", "status", "submitted_at", "google_opened_at")
    list_filter = ("status", "location__domain", "overall_rating")
    search_fields = ("anonymous_session_token", "location__name")
    readonly_fields = ("anonymous_session_token", "started_at", "created_at", "updated_at")
    inlines = [AnswerInline, DraftInline]


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("session", "event_type", "created_at")
    list_filter = ("event_type",)
    readonly_fields = ("session", "event_type", "idempotency_key", "metadata", "created_at")
