import django.db.models.deletion
from django.db import migrations, models

import apps.locations.models
import apps.locations.validators


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0001_initial"), ("catalog", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=180)),
                ("google_review_url", models.URLField(max_length=1000, validators=[apps.locations.validators.validate_google_review_url])),
                ("google_link_verified_at", models.DateTimeField(blank=True, null=True)),
                ("public_qr_token", models.CharField(default=apps.locations.models.qr_token, editable=False, max_length=80, unique=True)),
                ("active", models.BooleanField(default=True)),
                ("default_language", models.CharField(default="en", max_length=10)),
                ("logo_url", models.URLField(blank=True)),
                ("domain", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="locations", to="catalog.domain")),
                ("merchant_account", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="location", to="accounts.merchantaccount")),
            ],
        )
    ]
