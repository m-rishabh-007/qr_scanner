import secrets

from django.db import models

from apps.accounts.models import MerchantAccount
from apps.catalog.models import Domain
from apps.core.models import TimeStampedModel

from .validators import validate_google_review_url


def qr_token() -> str:
    return secrets.token_urlsafe(32)


class Location(TimeStampedModel):
    merchant_account = models.OneToOneField(
        MerchantAccount, on_delete=models.CASCADE, related_name="location"
    )
    name = models.CharField(max_length=180)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT, related_name="locations")
    google_review_url = models.URLField(max_length=1000, validators=[validate_google_review_url])
    google_link_verified_at = models.DateTimeField(null=True, blank=True)
    public_qr_token = models.CharField(max_length=80, unique=True, default=qr_token, editable=False)
    active = models.BooleanField(default=True)
    default_language = models.CharField(max_length=10, default="en")
    logo_url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.name
