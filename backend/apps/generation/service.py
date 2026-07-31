from django.conf import settings

from apps.catalog.models import DomainPromptVersion
from apps.feedback.models import FeedbackSession
from .client import GenerationResult, LiteLLMGenerationClient
from .exceptions import GenerationError


class ReviewGenerationService:
    def __init__(self, client: LiteLLMGenerationClient | None = None):
        self.client = client or LiteLLMGenerationClient()

    def _payload(self, session: FeedbackSession) -> dict:
        ratings = {
            answer.question.aspect_id: answer.rating
            for answer in session.answers.select_related("question").all()
        }
        return {
            "domain": session.location.domain.slug,
            "location_name": session.location.name,
            "ratings": ratings,
            "additional_comment": session.optional_comment,
            "output_language": session.language,
            "output_contract": {
                "drafts": [
                    {"type": "short", "length": "1-2 sentences"},
                    {"type": "natural", "length": "2-3 sentences"},
                    {"type": "detailed", "length": "3-5 sentences"},
                ]
            },
        }

    def generate(self, session: FeedbackSession) -> tuple[GenerationResult, DomainPromptVersion, int]:
        prompt = (
            DomainPromptVersion.objects.filter(
                domain=session.location.domain,
                language_code=session.language,
                active=True,
            )
            .order_by("-version")
            .first()
        )
        if not prompt and session.language != session.location.domain.default_language:
            prompt = (
                DomainPromptVersion.objects.filter(
                    domain=session.location.domain,
                    language_code=session.location.domain.default_language,
                    active=True,
                )
                .order_by("-version")
                .first()
            )
        if not prompt:
            raise GenerationError("No active prompt exists for this domain and language")
        model = prompt.model_override or settings.LITELLM_MODEL
        last_error: Exception | None = None
        for attempt in (1, 2):
            try:
                result = self.client.generate(
                    system_prompt=prompt.system_prompt,
                    user_payload=self._payload(session),
                    model=model,
                )
                return result, prompt, attempt
            except GenerationError as exc:
                last_error = exc
        raise GenerationError("Generation failed after one controlled retry") from last_error
