from django.db import IntegrityError

from .models import AnalyticsEvent, FeedbackSession


def record_event(
    session: FeedbackSession,
    event_type: str,
    *,
    idempotency_key: str = "",
    metadata: dict | None = None,
) -> AnalyticsEvent:
    try:
        event, _ = AnalyticsEvent.objects.get_or_create(
            session=session,
            event_type=event_type,
            idempotency_key=idempotency_key,
            defaults={"metadata": metadata or {}},
        )
        return event
    except IntegrityError:
        return AnalyticsEvent.objects.get(
            session=session, event_type=event_type, idempotency_key=idempotency_key
        )
