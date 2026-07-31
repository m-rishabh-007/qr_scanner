from django.urls import path

from .views import deletion, home, password_reset_page, privacy, review_flow, verify_email_page

urlpatterns = [
    path("", home, name="home"),
    path("r/<str:qr_token>/", review_flow, name="review-flow"),
    path("privacy/", privacy, name="privacy"),
    path("account-deletion/", deletion, name="account-deletion"),
    path("verify-email", verify_email_page, name="verify-email-page"),
    path("reset-password", password_reset_page, name="password-reset-page"),
]
