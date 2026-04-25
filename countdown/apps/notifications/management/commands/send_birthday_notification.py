"""
Management command to send daily birthday notification emails.
Uses the centralized birthday calculation service.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.birthdays.models import Birthday
from apps.birthdays.services import calculate_countdown
from apps.notifications.models import NotificationSubscription
from apps.notifications.services import send_birthday_notification


class Command(BaseCommand):
    help = 'Send daily birthday notification emails to all active subscribers'

    def handle(self, *args, **options):
        today = timezone.now().date()
        self.stdout.write(f"Processing birthday notifications for {today}...")

        # Get all organizations with active subscribers
        org_ids = (
            NotificationSubscription.objects
            .filter(is_active=True)
            .values_list('organization_id', flat=True)
            .distinct()
        )

        total_sent = 0
        total_failed = 0

        for org_id in org_ids:
            todays = []
            upcoming = []

            birthdays = Birthday.objects.filter(
                organization_id=org_id,
                is_active=True,
            )

            for b in birthdays:
                countdown = calculate_countdown(b.date_of_birth)
                formatted_date = countdown.next_birthday.strftime("%A, %B %d")

                if countdown.is_today:
                    todays.append({
                        'name': b.full_name,
                        'date': formatted_date,
                    })
                elif 1 <= countdown.days <= 3:
                    upcoming.append({
                        'name': b.full_name,
                        'date': formatted_date,
                        'days_until': countdown.days,
                    })

            # Only send if there's something to report
            if not todays and not upcoming:
                continue

            subscribers = NotificationSubscription.objects.filter(
                organization_id=org_id,
                is_active=True,
            )

            for sub in subscribers:
                success = send_birthday_notification(
                    subscription=sub,
                    todays_birthdays=todays,
                    upcoming_birthdays=upcoming,
                )

                if success:
                    total_sent += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Sent to {sub.email}"))
                else:
                    total_failed += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Failed: {sub.email}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Sent: {total_sent}, Failed: {total_failed}"
            )
        )
