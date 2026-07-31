import pytest

from apps.generation.client import _validate_payload
from apps.generation.exceptions import MalformedGenerationError


def test_generation_requires_exact_styles():
    with pytest.raises(MalformedGenerationError):
        _validate_payload({"drafts": [{"type": "short", "text": "Only one"}]})


def test_generation_accepts_three_distinct_styles():
    result = _validate_payload(
        {"drafts": [
            {"type": "short", "text": "Short."},
            {"type": "natural", "text": "Natural text."},
            {"type": "detailed", "text": "Detailed text with more context."},
        ]}
    )
    assert [item.style for item in result] == ["short", "natural", "detailed"]
