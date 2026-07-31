from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import MerchantAccount
from apps.catalog.models import Domain
from apps.feedback.models import AnalyticsEvent, FeedbackSession
from apps.generation.client import DraftPayload, GenerationResult
from apps.locations.models import Location

User = get_user_model()


@pytest.fixture
def location(seeded_catalog):
    user = User.objects.create_user(email="owner@example.com", password="password", email_verified=True)
    account = MerchantAccount.objects.create(user=user, business_name="Cafe", status=MerchantAccount.Status.APPROVED)
    return Location.objects.create(
        merchant_account=account,
        name="Cafe",
        domain=Domain.objects.get(slug="restaurant"),
        google_review_url="https://g.page/r/example/review",
    )


@pytest.mark.django_db
def test_complete_public_flow_records_google_open(location):
    client = APIClient()
    created = client.post(f"/api/public/qr/{location.public_qr_token}/sessions/", {}, format="json")
    assert created.status_code == 201
    token = created.data["session_token"]
    questions = list(location.domain.questions.filter(active=True))
    submitted = client.post(
        f"/api/public/sessions/{token}/feedback/",
        {
            "answers": [{"question_id": q.id, "rating": 4} for q in questions],
            "optional_comment": "Good food, but the wait was longer than expected.",
            "idempotency_key": "feedback-1",
        },
        format="json",
    )
    assert submitted.status_code == 200

    fake_result = GenerationResult(
        drafts=[
            DraftPayload("short", "Good food, though the wait was longer than expected."),
            DraftPayload("natural", "I enjoyed the food. The wait was longer than expected, but the overall experience was good."),
            DraftPayload("detailed", "I had a good overall experience and enjoyed the food. The wait was longer than expected, which is worth improving. The rest of the visit matched my ratings."),
        ],
        model_identifier="test-model",
        duration_ms=25,
    )
    prompt = location.domain.prompt_versions.get(active=True)
    with patch("apps.feedback.views.ReviewGenerationService.generate", return_value=(fake_result, prompt, 1)):
        generated = client.post(f"/api/public/sessions/{token}/generate/", {}, format="json")
    assert generated.status_code == 200
    assert [d["style"] for d in generated.data["drafts"]] == ["short", "natural", "detailed"]

    draft = generated.data["drafts"][1]
    selected = client.post(
        f"/api/public/sessions/{token}/select/",
        {"draft_id": draft["id"], "final_text": draft["text"]},
        format="json",
    )
    assert selected.status_code == 200
    opened = client.post(
        f"/api/public/sessions/{token}/events/",
        {"event_type": "google_open_clicked", "idempotency_key": "open-1"},
        format="json",
    )
    assert opened.status_code == 204
    session = FeedbackSession.objects.get(anonymous_session_token=token)
    assert session.google_opened_at is not None
    assert AnalyticsEvent.objects.filter(session=session, event_type="google_open_clicked").count() == 1
