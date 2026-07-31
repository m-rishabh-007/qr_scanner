import os
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError, call_command
from django.utils import timezone

from apps.accounts.models import MerchantAccount
from apps.catalog.models import Domain
from apps.feedback.models import AnalyticsEvent, FeedbackAnswer, FeedbackSession
from apps.feedback.services import record_event
from apps.locations.models import Location


class Command(BaseCommand):
    help = "Create an approved reviewer/demo merchant with sample analytics. Requires explicit env credentials."

    def handle(self, *args, **options):
        email = os.getenv("DEMO_MERCHANT_EMAIL")
        password = os.getenv("DEMO_MERCHANT_PASSWORD")
        review_url = os.getenv("DEMO_GOOGLE_REVIEW_URL", "https://g.page/r/example/review")
        if not email or not password:
            raise CommandError("Set DEMO_MERCHANT_EMAIL and DEMO_MERCHANT_PASSWORD explicitly.")
        call_command("seed_initial_catalog", verbosity=0)
        user, created = get_user_model().objects.get_or_create(
            email=email.lower(), defaults={"email_verified": True, "is_active": True}
        )
        user.email_verified = True
        user.is_active = True
        user.set_password(password)
        user.save()
        account, _ = MerchantAccount.objects.update_or_create(
            user=user,
            defaults={
                "business_name": "ReviewFlow Demo Restaurant",
                "status": MerchantAccount.Status.APPROVED,
                "approved_at": timezone.now(),
            },
        )
        domain = Domain.objects.get(slug="restaurant")
        location, _ = Location.objects.update_or_create(
            merchant_account=account,
            defaults={
                "name": "ReviewFlow Demo Restaurant",
                "domain": domain,
                "google_review_url": review_url,
                "google_link_verified_at": timezone.now(),
                "active": True,
            },
        )
        if location.feedback_sessions.exists():
            self.stdout.write(self.style.WARNING("Demo feedback already exists; not duplicating it."))
            return
        questions = list(domain.questions.filter(active=True))
        for index in range(24):
            created_at = timezone.now() - timedelta(days=index % 18, hours=index)
            session = FeedbackSession.objects.create(
                location=location,
                submitted_at=created_at,
                overall_rating=[5, 4, 4, 3, 5, 2][index % 6],
                optional_comment="Sample feedback for Play reviewer inspection.",
                status=FeedbackSession.Status.COMPLETED if index % 3 != 0 else FeedbackSession.Status.SUBMITTED,
                google_opened_at=created_at if index % 3 != 0 else None,
            )
            FeedbackSession.objects.filter(pk=session.pk).update(created_at=created_at, started_at=created_at)
            for question in questions:
                base = session.overall_rating or 3
                FeedbackAnswer.objects.create(
                    session=session,
                    question=question,
                    rating=max(1, min(5, base + random.choice([-1, 0, 0, 1]))),
                )
            for event in [
                AnalyticsEvent.EventType.QR_SCANNED,
                AnalyticsEvent.EventType.FORM_STARTED,
                AnalyticsEvent.EventType.FEEDBACK_SUBMITTED,
                AnalyticsEvent.EventType.GENERATION_REQUESTED,
                AnalyticsEvent.EventType.GENERATION_SUCCEEDED,
                AnalyticsEvent.EventType.DRAFT_SELECTED,
                AnalyticsEvent.EventType.COPY_SUCCEEDED,
            ]:
                record_event(session, event, idempotency_key=f"demo-{index}-{event}")
            if session.google_opened_at:
                record_event(
                    session,
                    AnalyticsEvent.EventType.GOOGLE_OPEN_CLICKED,
                    idempotency_key=f"demo-{index}-google",
                )
        self.stdout.write(self.style.SUCCESS(f"Created demo merchant {email}"))
