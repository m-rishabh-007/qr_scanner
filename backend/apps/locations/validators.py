from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_google_review_url(value: str) -> None:
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    path = parsed.path or "/"
    if parsed.scheme != "https":
        raise ValidationError("Google review URL must use HTTPS.")
    if host not in settings.GOOGLE_REVIEW_ALLOWED_HOSTS:
        raise ValidationError("Unsupported Google review host.")
    if parsed.username or parsed.password:
        raise ValidationError("Credentials are not allowed in the URL.")
    if host == "search.google.com" and not path.startswith("/local/writereview"):
        raise ValidationError("The Google link is not a supported write-review path.")
    if host in {"www.google.com", "maps.google.com"} and not (
        path.startswith("/maps") or path.startswith("/local/writereview") or "writereview" in parsed.query
    ):
        raise ValidationError("The Google link is not a supported Maps/review path.")
    if host in {"g.page", "maps.app.goo.gl", "goo.gl"} and path == "/":
        raise ValidationError("The shortened Google review link is incomplete.")
