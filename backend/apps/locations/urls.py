from django.urls import path

from .views import DomainOptionsView, MerchantLocationView, QrPngView, RotateQrTokenView, VerifyGoogleLinkView

urlpatterns = [
    path("domains/", DomainOptionsView.as_view()),
    path("location/", MerchantLocationView.as_view()),
    path("location/verify-google-link/", VerifyGoogleLinkView.as_view()),
    path("location/qr.png", QrPngView.as_view()),
    path("location/rotate-qr/", RotateQrTokenView.as_view()),
]
