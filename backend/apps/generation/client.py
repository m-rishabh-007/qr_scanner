import json
import threading
import time
from dataclasses import dataclass

import httpx
from django.conf import settings

from .exceptions import GenerationError, MalformedGenerationError


@dataclass(frozen=True)
class DraftPayload:
    style: str
    text: str


@dataclass(frozen=True)
class GenerationResult:
    drafts: list[DraftPayload]
    model_identifier: str
    duration_ms: int


_ALLOWED_STYLES = ["short", "natural", "detailed"]
_semaphore = threading.BoundedSemaphore(settings.LITELLM_MAX_CONCURRENCY)


def _extract_json(content: str) -> dict:
    value = content.strip()
    if value.startswith("```"):
        value = value.strip("`")
        if value.startswith("json"):
            value = value[4:].lstrip()
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        start, end = value.find("{"), value.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(value[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise MalformedGenerationError("Model did not return valid JSON") from exc


def _validate_payload(payload: dict) -> list[DraftPayload]:
    rows = payload.get("drafts")
    if not isinstance(rows, list) or len(rows) != 3:
        raise MalformedGenerationError("Exactly three drafts are required")
    by_style: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise MalformedGenerationError("Draft entries must be objects")
        style = row.get("type") or row.get("style")
        text = row.get("text")
        if style not in _ALLOWED_STYLES or not isinstance(text, str):
            raise MalformedGenerationError("Invalid draft style or text")
        text = " ".join(text.split()).strip()
        if not text or len(text) > settings.MAX_REVIEW_LENGTH:
            raise MalformedGenerationError("Draft text length is invalid")
        by_style[style] = text
    if set(by_style) != set(_ALLOWED_STYLES):
        raise MalformedGenerationError("Draft styles must be short, natural and detailed")
    return [DraftPayload(style=s, text=by_style[s]) for s in _ALLOWED_STYLES]


class LiteLLMGenerationClient:
    def generate(self, *, system_prompt: str, user_payload: dict, model: str) -> GenerationResult:
        headers = {"Content-Type": "application/json"}
        if settings.LITELLM_API_KEY:
            headers["Authorization"] = f"Bearer {settings.LITELLM_API_KEY}"
        request_payload = {
            "model": model,
            "temperature": settings.LITELLM_TEMPERATURE,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False, separators=(",", ":")),
                },
            ],
        }
        started = time.monotonic()
        acquired = _semaphore.acquire(timeout=settings.LITELLM_TIMEOUT_SECONDS)
        if not acquired:
            raise GenerationError("Model concurrency limit reached")
        try:
            try:
                with httpx.Client(timeout=settings.LITELLM_TIMEOUT_SECONDS) as client:
                    response = client.post(
                        f"{settings.LITELLM_BASE_URL}/chat/completions",
                        headers=headers,
                        json=request_payload,
                    )
                    response.raise_for_status()
            except (httpx.TimeoutException, httpx.HTTPError) as exc:
                raise GenerationError("LiteLLM request failed") from exc
        finally:
            _semaphore.release()
        duration_ms = int((time.monotonic() - started) * 1000)
        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise MalformedGenerationError("LiteLLM response shape is invalid") from exc
        return GenerationResult(
            drafts=_validate_payload(_extract_json(content)),
            model_identifier=model,
            duration_ms=duration_ms,
        )
