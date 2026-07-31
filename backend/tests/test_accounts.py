import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import MerchantAccount

User = get_user_model()


@pytest.mark.django_db
def test_registration_requires_verification_and_approval():
    client = APIClient()
    response = client.post(
        "/api/auth/register/",
        {"email": "owner@example.com", "password": "A-strong-password-123", "business_name": "Example"},
        format="json",
    )
    assert response.status_code == 201
    user = User.objects.get(email="owner@example.com")
    assert user.email_verified is False
    assert user.merchant_account.status == MerchantAccount.Status.PENDING

    login = client.post(
        "/api/auth/login/",
        {"email": user.email, "password": "A-strong-password-123"},
        format="json",
    )
    assert login.status_code == 400


@pytest.mark.django_db
def test_approved_verified_merchant_can_login():
    user = User.objects.create_user(
        email="approved@example.com", password="A-strong-password-123", email_verified=True
    )
    MerchantAccount.objects.create(
        user=user, business_name="Approved", status=MerchantAccount.Status.APPROVED
    )
    response = APIClient().post(
        "/api/auth/login/",
        {"email": user.email, "password": "A-strong-password-123"},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]
