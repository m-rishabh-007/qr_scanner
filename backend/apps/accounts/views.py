from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .emails import send_verification_email
from .models import AccountDeletionRequest
from .serializers import (
    ApprovedTokenObtainPairSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegistrationSerializer,
)
from .tokens import read_email_verification_token

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user)
        return Response(
            {"detail": "Registration created. Verify email and wait for merchant approval."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        token = request.data.get("token", "")
        try:
            user = User.objects.get(pk=read_email_verification_token(token))
        except Exception:
            return Response({"detail": "Invalid or expired token."}, status=400)
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        return Response({"detail": "Email verified. Approval may still be pending."})


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = ApprovedTokenObtainPairSerializer


class LogoutView(APIView):
    def post(self, request):
        token = request.data.get("refresh")
        if token:
            RefreshToken(token).blacklist()
        return Response(status=204)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.validated_data["email"].lower()).first()
        if user and user.is_active:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            url = f"{settings.PUBLIC_BASE_URL}/reset-password?uid={uid}&token={token}"
            send_mail(
                f"Reset your {settings.PRODUCT_NAME} password",
                f"Open this link to reset your password: {url}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        return Response({"detail": "If the account exists, a reset email was sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user_id = urlsafe_base64_decode(serializer.validated_data["uid"]).decode()
            user = User.objects.get(pk=user_id)
        except Exception:
            return Response({"detail": "Invalid reset request."}, status=400)
        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            return Response({"detail": "Invalid or expired reset token."}, status=400)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated."})


class DeleteAccountView(APIView):
    def post(self, request):
        password = request.data.get("password", "")
        if not request.user.check_password(password):
            return Response({"detail": "Password is incorrect."}, status=400)
        AccountDeletionRequest.objects.create(
            user=request.user,
            requested_reason=str(request.data.get("reason", ""))[:1000],
        )
        request.user.is_active = False
        request.user.save(update_fields=["is_active"])
        return Response(status=204)
