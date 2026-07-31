import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import MerchantAccount
from apps.catalog.models import Domain
from apps.locations.models import Location

User = get_user_model()


def approved_client():
    user = User.objects.create_user(email="merchant@example.com", password="A-password-123", email_verified=True)
    MerchantAccount.objects.create(user=user, business_name="Merchant", status=MerchantAccount.Status.APPROVED)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")
    return client, user


@pytest.mark.django_db
def test_one_account_one_location_and_google_allowlist(seeded_catalog):
    client, user = approved_client()
    domain = Domain.objects.get(slug="restaurant")
    bad = client.post(
        "/api/merchant/location/",
        {"name": "Cafe", "domain_id": domain.id, "google_review_url": "https://evil.example/phish"},
        format="json",
    )
    assert bad.status_code == 400

    good = client.post(
        "/api/merchant/location/",
        {"name": "Cafe", "domain_id": domain.id, "google_review_url": "https://g.page/r/example/review"},
        format="json",
    )
    assert good.status_code == 201
    assert Location.objects.filter(merchant_account=user.merchant_account).count() == 1

    duplicate = client.post(
        "/api/merchant/location/",
        {"name": "Second", "domain_id": domain.id, "google_review_url": "https://g.page/r/example2/review"},
        format="json",
    )
    assert duplicate.status_code == 409
