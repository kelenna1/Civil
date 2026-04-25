"""
Email notification services using Resend.
Sends birthday alerts and welcome emails using Django templates
instead of inline HTML strings.
"""

import logging
import resend
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)

# Configure Resend API key
resend.api_key = settings.RESEND_API_KEY


def _get_site_url():
    """Get the current site URL for use in emails."""
    try:
        site = Site.objects.get_current()
        domain = site.domain
        if not domain.startswith('http'):
            domain = f"https://{domain}"
        return domain
    except Exception:
        return 'https://candlesdown.onrender.com'


def send_birthday_notification(subscription, todays_birthdays, upcoming_birthdays=None):
    """
    Send birthday notification email.
    
    Args:
        subscription: NotificationSubscription instance
        todays_birthdays: List of dicts with 'name' and 'date' keys
        upcoming_birthdays: Optional list of dicts with 'name', 'date', 'days_until' keys
    
    Returns:
        bool: True if email was sent successfully
    """
    if not todays_birthdays and not upcoming_birthdays:
        return False

    site_url = _get_site_url()
    unsubscribe_url = f"{site_url}{reverse('unsubscribe', args=[subscription.unsubscribe_token])}"

    # Build subject line
    if todays_birthdays:
        names = ", ".join(b['name'] for b in todays_birthdays[:2])
        subject = f"🎂 Today's Birthdays: {names}"
        if len(todays_birthdays) > 2:
            subject += " and more!"
    else:
        subject = f"📅 Upcoming Birthdays in {subscription.organization.name}"

    # Render email template
    html_content = render_to_string('emails/birthday_notification.html', {
        'org_name': subscription.organization.name,
        'todays_birthdays': todays_birthdays,
        'upcoming_birthdays': upcoming_birthdays,
        'dashboard_url': f"{site_url}/dashboard/",
        'unsubscribe_url': unsubscribe_url,
    })

    try:
        resend.Emails.send({
            "from": f"CandlesDown <{settings.RESEND_FROM_EMAIL}>",
            "to": [subscription.email],
            "subject": subject,
            "html": html_content,
        })
        logger.info(f"Birthday notification sent to {subscription.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send birthday notification to {subscription.email}: {e}")
        return False


def send_welcome_email(subscription):
    """
    Send welcome email to a new subscriber.
    
    Args:
        subscription: NotificationSubscription instance
    
    Returns:
        bool: True if email was sent successfully
    """
    site_url = _get_site_url()
    unsubscribe_url = f"{site_url}{reverse('unsubscribe', args=[subscription.unsubscribe_token])}"

    html_content = render_to_string('emails/welcome.html', {
        'org_name': subscription.organization.name,
        'dashboard_url': f"{site_url}/dashboard/",
        'unsubscribe_url': unsubscribe_url,
    })

    try:
        resend.Emails.send({
            "from": f"CandlesDown <{settings.RESEND_FROM_EMAIL}>",
            "to": [subscription.email],
            "subject": "🎉 You're Subscribed to Birthday Alerts!",
            "html": html_content,
        })
        logger.info(f"Welcome email sent to {subscription.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {subscription.email}: {e}")
        return False
