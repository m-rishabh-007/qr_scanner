from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.core.models import TimeStampedModel


def default_supported_languages() -> list[str]:
    return ["en"]


class Domain(TimeStampedModel):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    default_language = models.CharField(max_length=10, default="en")
    supported_languages = models.JSONField(default=default_supported_languages)
    questionnaire_version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Question(TimeStampedModel):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="questions")
    aspect_id = models.SlugField(max_length=80)
    display_label = models.CharField(max_length=120)
    description = models.CharField(max_length=280, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    required = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    minimum_rating = models.PositiveSmallIntegerField(default=1)
    maximum_rating = models.PositiveSmallIntegerField(default=5)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["domain", "aspect_id"], name="unique_domain_aspect")
        ]

    def clean(self):
        if self.minimum_rating >= self.maximum_rating:
            raise ValidationError("maximum_rating must be greater than minimum_rating")

    def __str__(self) -> str:
        return f"{self.domain.name}: {self.display_label}"


class QuestionTranslation(TimeStampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="translations")
    language_code = models.CharField(max_length=10)
    display_label = models.CharField(max_length=120)
    description = models.CharField(max_length=280, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["question", "language_code"], name="unique_question_language")
        ]

    def __str__(self) -> str:
        return f"{self.question.aspect_id} ({self.language_code})"


class DomainPromptVersion(TimeStampedModel):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="prompt_versions")
    language_code = models.CharField(max_length=10, default="en")
    version = models.PositiveIntegerField()
    system_prompt = models.TextField()
    active = models.BooleanField(default=False)
    model_override = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["domain", "-version"]
        constraints = [
            models.UniqueConstraint(fields=["domain", "language_code", "version"], name="unique_domain_prompt_version")
        ]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.active:
                DomainPromptVersion.objects.filter(domain=self.domain, language_code=self.language_code, active=True).exclude(
                    pk=self.pk
                ).update(active=False)
            super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.domain.name} {self.language_code} v{self.version}{' (active)' if self.active else ''}"
