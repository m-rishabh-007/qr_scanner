import django.db.models.deletion
from django.db import migrations, models

import apps.catalog.models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Domain",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("slug", models.SlugField(unique=True)),
                ("name", models.CharField(max_length=80)),
                ("description", models.TextField(blank=True)),
                ("active", models.BooleanField(default=True)),
                ("default_language", models.CharField(default="en", max_length=10)),
                ("supported_languages", models.JSONField(default=apps.catalog.models.default_supported_languages)),
                ("questionnaire_version", models.PositiveIntegerField(default=1)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="DomainPromptVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("language_code", models.CharField(default="en", max_length=10)),
                ("version", models.PositiveIntegerField()),
                ("system_prompt", models.TextField()),
                ("active", models.BooleanField(default=False)),
                ("model_override", models.CharField(blank=True, max_length=120)),
                ("notes", models.TextField(blank=True)),
                ("domain", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prompt_versions", to="catalog.domain")),
            ],
            options={"ordering": ["domain", "-version"]},
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("aspect_id", models.SlugField(max_length=80)),
                ("display_label", models.CharField(max_length=120)),
                ("description", models.CharField(blank=True, max_length=280)),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("required", models.BooleanField(default=True)),
                ("active", models.BooleanField(default=True)),
                ("minimum_rating", models.PositiveSmallIntegerField(default=1)),
                ("maximum_rating", models.PositiveSmallIntegerField(default=5)),
                ("domain", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="catalog.domain")),
            ],
            options={"ordering": ["order", "id"]},
        ),
        migrations.CreateModel(
            name="QuestionTranslation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("language_code", models.CharField(max_length=10)),
                ("display_label", models.CharField(max_length=120)),
                ("description", models.CharField(blank=True, max_length=280)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="translations", to="catalog.question")),
            ],
        ),
        migrations.AddConstraint(model_name="questiontranslation", constraint=models.UniqueConstraint(fields=("question", "language_code"), name="unique_question_language")),
        migrations.AddConstraint(model_name="domainpromptversion", constraint=models.UniqueConstraint(fields=("domain", "language_code", "version"), name="unique_domain_prompt_version")),
        migrations.AddConstraint(model_name="question", constraint=models.UniqueConstraint(fields=("domain", "aspect_id"), name="unique_domain_aspect")),
    ]
