from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import MerchantAccount

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=10)
    business_name = serializers.CharField(max_length=180)

    def validate_email(self, value: str) -> str:
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data):
        business_name = validated_data.pop("business_name")
        user = User.objects.create_user(**validated_data)
        MerchantAccount.objects.create(user=user, business_name=business_name)
        return user


class ApprovedTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if not user.email_verified:
            raise serializers.ValidationError("Email verification is required.")
        account = getattr(user, "merchant_account", None)
        if not account or account.status != MerchantAccount.Status.APPROVED:
            raise serializers.ValidationError("Merchant approval is required.")
        data["user"] = {"email": user.email, "business_name": account.business_name}
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=10, write_only=True)

    def validate_new_password(self, value: str) -> str:
        validate_password(value)
        return value
