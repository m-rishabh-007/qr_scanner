from rest_framework import serializers

from apps.catalog.models import Domain

from .models import Location
from .validators import validate_google_review_url


class DomainOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ["id", "slug", "name"]


class LocationSerializer(serializers.ModelSerializer):
    domain = DomainOptionSerializer(read_only=True)
    domain_id = serializers.PrimaryKeyRelatedField(
        source="domain", queryset=Domain.objects.filter(active=True), write_only=True
    )
    public_url = serializers.SerializerMethodField()
    qr_png_url = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "domain",
            "domain_id",
            "google_review_url",
            "google_link_verified_at",
            "public_qr_token",
            "active",
            "default_language",
            "logo_url",
            "public_url",
            "qr_png_url",
        ]
        read_only_fields = ["id", "public_qr_token", "google_link_verified_at"]

    def get_public_url(self, obj):
        request = self.context.get("request")
        path = f"/r/{obj.public_qr_token}/"
        return request.build_absolute_uri(path) if request else path

    def get_qr_png_url(self, obj):
        request = self.context.get("request")
        path = "/api/merchant/location/qr.png"
        return request.build_absolute_uri(path) if request else path

    def validate_google_review_url(self, value):
        validate_google_review_url(value)
        return value

    def update(self, instance, validated_data):
        if "google_review_url" in validated_data and validated_data["google_review_url"] != instance.google_review_url:
            instance.google_link_verified_at = None
        return super().update(instance, validated_data)
