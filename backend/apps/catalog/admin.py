from django.contrib import admin

from .models import Domain, DomainPromptVersion, Question, QuestionTranslation


class QuestionTranslationInline(admin.TabularInline):
    model = QuestionTranslation
    extra = 0


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ("aspect_id", "display_label", "description", "order", "required", "active")


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "active", "questionnaire_version", "default_language")
    list_filter = ("active", "default_language")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionTranslationInline]
    list_display = ("display_label", "domain", "aspect_id", "order", "required", "active")
    list_filter = ("domain", "required", "active")
    ordering = ("domain", "order")


@admin.register(DomainPromptVersion)
class DomainPromptVersionAdmin(admin.ModelAdmin):
    list_display = ("domain", "language_code", "version", "active", "model_override", "created_at")
    list_filter = ("domain", "language_code", "active")
