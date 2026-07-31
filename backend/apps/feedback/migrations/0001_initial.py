import django.db.models.deletion
from django.db import migrations, models

import apps.feedback.models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("catalog", "0001_initial"), ("locations", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="FeedbackSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("anonymous_session_token", models.CharField(default=apps.feedback.models.session_token, editable=False, max_length=80, unique=True)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("overall_rating", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("optional_comment", models.TextField(blank=True)),
                ("final_review_text", models.TextField(blank=True)),
                ("google_opened_at", models.DateTimeField(blank=True, null=True)),
                ("generation_count", models.PositiveSmallIntegerField(default=0)),
                ("status", models.CharField(choices=[("started", "Started"), ("submitted", "Feedback submitted"), ("generated", "Drafts generated"), ("completed", "Google opened"), ("abandoned", "Abandoned")], default="started", max_length=20)),
                ("language", models.CharField(default="en", max_length=10)),
                ("feedback_idempotency_key", models.CharField(blank=True, max_length=80)),
                ("location", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="feedback_sessions", to="locations.location")),
            ],
        ),
        migrations.CreateModel(
            name="GeneratedDraft",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("style", models.CharField(choices=[("short", "Short"), ("natural", "Natural"), ("detailed", "Detailed")], max_length=20)),
                ("text", models.TextField()),
                ("model_identifier", models.CharField(max_length=180)),
                ("generation_duration_ms", models.PositiveIntegerField(default=0)),
                ("generation_attempt", models.PositiveSmallIntegerField(default=1)),
                ("prompt_version", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="generated_drafts", to="catalog.domainpromptversion")),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="drafts", to="feedback.feedbacksession")),
            ],
        ),
        migrations.AddField(
            model_name="feedbacksession",
            name="selected_draft",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="selected_by_sessions", to="feedback.generateddraft"),
        ),
        migrations.CreateModel(
            name="FeedbackAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("rating", models.PositiveSmallIntegerField()),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="answers", to="catalog.question")),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="feedback.feedbacksession")),
            ],
        ),
        migrations.CreateModel(
            name="AnalyticsEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_type", models.CharField(choices=[("qr_scanned", "QR scanned"), ("form_started", "Form started"), ("feedback_submitted", "Feedback submitted"), ("generation_requested", "Generation requested"), ("generation_succeeded", "Generation succeeded"), ("generation_failed", "Generation failed"), ("draft_selected", "Draft selected"), ("draft_edited", "Draft edited"), ("copy_succeeded", "Copy succeeded"), ("copy_failed", "Copy failed"), ("google_open_clicked", "Google opened")], max_length=40)),
                ("idempotency_key", models.CharField(blank=True, max_length=100)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="feedback.feedbacksession")),
            ],
        ),
        migrations.AddIndex(model_name="feedbacksession", index=models.Index(fields=["location", "created_at"], name="feedback_fe_locatio_4a2e41_idx")),
        migrations.AddIndex(model_name="feedbacksession", index=models.Index(fields=["anonymous_session_token"], name="feedback_fe_anonymo_7c9ae5_idx")),
        migrations.AddConstraint(model_name="generateddraft", constraint=models.UniqueConstraint(fields=("session", "style", "generation_attempt"), name="unique_session_style_attempt")),
        migrations.AddConstraint(model_name="feedbackanswer", constraint=models.UniqueConstraint(fields=("session", "question"), name="unique_session_question")),
        migrations.AddIndex(model_name="analyticsevent", index=models.Index(fields=["session", "event_type", "created_at"], name="feedback_an_session_8a742d_idx")),
        migrations.AddConstraint(model_name="analyticsevent", constraint=models.UniqueConstraint(condition=~models.Q(idempotency_key=""), fields=("session", "event_type", "idempotency_key"), name="unique_idempotent_event")),
    ]
