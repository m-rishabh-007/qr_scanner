from django.conf import settings
from django.core import signing

EMAIL_VERIFY_SALT = "accounts.email.verify"


def make_email_verification_token(user_id: int) -> str:
    return signing.dumps({"user_id": user_id}, salt=EMAIL_VERIFY_SALT, compress=True)


def read_email_verification_token(token: str) -> int:
    payload = signing.loads(
        token,
        salt=EMAIL_VERIFY_SALT,
        max_age=settings.EMAIL_VERIFICATION_HOURS * 3600,
    )
    return int(payload["user_id"])
