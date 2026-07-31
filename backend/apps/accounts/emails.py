from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .tokens import make_email_verification_token


def send_verification_email(user) -> None:
    token = make_email_verification_token(user.pk)
    url = f"{settings.PUBLIC_BASE_URL}/verify-email?token={token}"
    body = render_to_string("emails/verify_email.txt", {"user": user, "url": url, "PRODUCT_NAME": settings.PRODUCT_NAME})
    send_mail(
        subject=f"Verify your {settings.PRODUCT_NAME} email",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
