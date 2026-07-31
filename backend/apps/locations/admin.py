from django.contrib import admin

from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "merchant_account", "domain", "active", "google_link_verified_at")
    list_filter = ("domain", "active")
    search_fields = ("name", "merchant_account__business_name", "public_qr_token")
    readonly_fields = ("public_qr_token", "google_link_verified_at")
