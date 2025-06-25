from django.core.management.base import BaseCommand
from django.utils import timezone
from birthday.models import Birthday, NotificationSubscription
from birthday.services import send_birthday_notification

class Command(BaseCommand):
    help = 'Sends birthday notifications with focus on today\'s birthdays'
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        self.stdout.write(f"Processing birthday notifications for {today}...")
        
        # Get all organizations with active subscribers
        organizations = NotificationSubscription.objects.filter(
            is_active=True
        ).values_list('organization', flat=True).distinct()
        
        for org_id in organizations:
            # Separate today's and upcoming birthdays
            todays = []
            upcoming = []
            
            for b in Birthday.objects.filter(organization_id=org_id, is_active=True):
                next_bday = b.date_of_birth.replace(year=today.year)
                if next_bday < today:
                    next_bday = next_bday.replace(year=today.year + 1)
                
                days_until = (next_bday - today).days
                formatted_date = next_bday.strftime("%A, %B %d")
                
                if days_until == 0:
                    todays.append({
                        'name': b.full_name,
                        'date': formatted_date
                    })
                elif 1 <= days_until <= 3:  # Show upcoming for next 3 days
                    upcoming.append({
                        'name': b.full_name,
                        'date': formatted_date,
                        'days_until': days_until
                    })
            
            # Only send if there are birthdays to report
            if todays or upcoming:
                subscribers = NotificationSubscription.objects.filter(
                    organization_id=org_id,
                    is_active=True
                )
                
                for sub in subscribers:
                    success = send_birthday_notification(
                        subscription=sub,
                        todays_birthdays=todays,
                        upcoming_birthdays=upcoming
                    )
                    
                    if success:
                        self.stdout.write(f"✓ Sent to {sub.email}")
                    else:
                        self.stdout.write(f"✗ Failed to send to {sub.email}")
        
        self.stdout.write("Notification process completed.")