import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode

from apps.accounts.tokens import read_email_verification_token

from apps.locations.models import Location


def home(request):
    return render(request, "public/home.html")


def review_flow(request, qr_token):
    location = (
        Location.objects.select_related("domain")
        .prefetch_related("domain__questions")
        .filter(public_qr_token=qr_token, active=True)
        .first()
    )
    if not location:
        raise Http404("This review link is unavailable.")
    questions = [
        {
            "id": q.id,
            "aspect_id": q.aspect_id,
            "label": q.display_label,
            "description": q.description,
            "required": q.required,
            "min": q.minimum_rating,
            "max": q.maximum_rating,
        }
        for q in location.domain.questions.filter(active=True).order_by("order")
    ]
    bootstrap = {
        "qrToken": location.public_qr_token,
        "locationName": location.name,
        "googleReviewUrl": location.google_review_url,
        "language": location.default_language,
        "questions": questions,
        "apiBase": "/api/public",
        "maxReviewLength": settings.MAX_REVIEW_LENGTH,
    }
    return render(
        request,
        "public/review_flow.html",
        {"location": location, "bootstrap_json": json.dumps(bootstrap)},
    )


def privacy(request):
    return render(request, "legal/privacy.html")


def deletion(request):
    return render(request, "legal/deletion.html")


def verify_email_page(request):
    token = request.GET.get("token", "")
    try:
        user = get_user_model().objects.get(pk=read_email_verification_token(token))
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        message = "Your email has been verified. Merchant approval may still be pending."
    except Exception:
        message = "This verification link is invalid or has expired."
    return render(request, "public/verify_email.html", {"message": message})


def password_reset_page(request):
    uid = request.GET.get("uid", "")
    token = request.GET.get("token", "")
    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = get_user_model().objects.get(pk=user_id)
    except Exception:
        return render(request, "public/reset_password.html", {"message": "Invalid reset link.", "show_form": False})
    if not default_token_generator.check_token(user, token):
        return render(request, "public/reset_password.html", {"message": "This reset link is invalid or has expired.", "show_form": False})
    if request.method == "POST":
        password = request.POST.get("password", "")
        confirmation = request.POST.get("password_confirm", "")
        if password != confirmation:
            return render(request, "public/reset_password.html", {"message": "Passwords do not match.", "show_form": True})
        try:
            validate_password(password, user)
        except ValidationError as exc:
            return render(request, "public/reset_password.html", {"message": " ".join(exc.messages), "show_form": True})
        user.set_password(password)
        user.save(update_fields=["password"])
        return render(request, "public/reset_password.html", {"message": "Password updated. Return to the merchant app to sign in.", "show_form": False})
    return render(request, "public/reset_password.html", {"show_form": True})
