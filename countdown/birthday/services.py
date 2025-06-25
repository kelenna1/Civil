import resend
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site

resend.api_key = settings.RESEND_API_KEY

def send_birthday_notification(subscription, todays_birthdays, upcoming_birthdays=None):
    """
    Send birthday notification email with:
    - Primary focus on today's birthdays
    - Optional section for upcoming birthdays (next 3 days)
    """
    current_site = Site.objects.get_current()
    org_name = subscription.organization.name
    
    # Build the email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
            .header {{ color: #d23c77; text-align: center; }}
            .today-section {{ background: #fff8f8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .upcoming-section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
            .birthday-item {{ margin: 12px 0; padding: 12px; background: white; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .today-item {{ border-left: 4px solid #d23c77; }}
            .upcoming-item {{ border-left: 4px solid #4a90e2; }}
            .birthday-name {{ font-weight: bold; color: #2c3e50; }}
            .today-badge {{ background: #d23c77; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 8px; }}
            .upcoming-badge {{ background: #4a90e2; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
            .action-link {{ display: block; text-align: center; margin: 25px 0; }}
            .button {{ background: #4a90e2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }}
            .unsubscribe {{ font-size: 12px; color: #999; text-align: center; margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <h1 class="header">🎉 Birthday Alert</h1>
    """
    
    # Today's Birthdays Section (Primary Focus)
    if todays_birthdays:
        html_content += f"""
        <div class="today-section">
            <h2>Today's Celebrations in {org_name}</h2>
            {"".join(
                f'<div class="birthday-item today-item">'
                f'<span class="birthday-name">{b["name"]}</span> '
                f'<span class="today-badge">TODAY</span>'
                f'<div style="margin-top: 8px;">🎂 Wishing {b["name"].split()[0]} a wonderful birthday!</div>'
                f'</div>'
                for b in todays_birthdays
            )}
        </div>
        """
    
    # Upcoming Birthdays Section (Secondary)
    if upcoming_birthdays:
        html_content += f"""
        <div class="upcoming-section">
            <h3>Coming Up Soon</h3>
            {"".join(
                f'<div class="birthday-item upcoming-item">'
                f'<span class="birthday-name">{b["name"]}</span> '
                f'<span class="upcoming-badge">in {b["days_until"]} day{"s" if b["days_until"] > 1 else ""}</span>'
                f'<div style="margin-top: 8px;">{b["date"]}</div>'
                f'</div>'
                for b in upcoming_birthdays
            )}
        </div>
        """
    
    # Footer with action links
    html_content += f"""
        <div class="action-link">
            <a href="https://candlesdown.onrender.com/dashboard/" class="button">
                View All Birthdays
            </a>
        </div>
        
        <div class="unsubscribe">
            <a href="{current_site.domain}{reverse('unsubscribe', args=[subscription.unsubscribe_token])}">
                Unsubscribe from these notifications
            </a>
        </div>
    </body>
    </html>
    """
    
    # Dynamic subject line
    if todays_birthdays:
        names = ", ".join(b['name'] for b in todays_birthdays[:2])
        subject = f"🎂 Today's Birthdays: {names}" + (" and more!" if len(todays_birthdays) > 2 else "")
    elif upcoming_birthdays:
        subject = f"Upcoming Birthdays in {org_name}"
    else:
        return False  # No birthdays to report
    
    try:
        resend.Emails.send({
            "from": f"CandlesDown <{settings.RESEND_FROM_EMAIL}>",
            "to": [subscription.email],
            "subject": subject,
            "html": html_content
        })
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    

def send_welcome_email(subscription):
    current_site = Site.objects.get_current()
    org_name = subscription.organization.name

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
            .header {{ color: #4a90e2; text-align: center; }}
            .message-section {{ background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .button {{ background: #4a90e2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-top: 15px; }}
            .unsubscribe {{ font-size: 12px; color: #999; text-align: center; margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <h1 class="header">🎉 Welcome to Birthday Notifications!</h1>
        <div class="message-section">
            <p>Thanks for subscribing to <strong>{org_name}</strong>'s birthday alerts!</p>
            <p>You'll receive timely emails whenever someone’s birthday is today or coming up soon.</p>
            <a href="https://candlesdown.onrender.com/dashboard/" class="button">View Dashboard</a>
        </div>

        <div class="unsubscribe">
            <a href="{current_site.domain}{reverse('unsubscribe', args=[subscription.unsubscribe_token])}">
                Unsubscribe from these notifications
            </a>
        </div>
    </body>
    </html>
    """

    try:
        resend.Emails.send({
            "from": f"CandlesDown <{settings.RESEND_FROM_EMAIL}>",
            "to": [subscription.email],
            "subject": "🎉 You're Subscribed to Birthday Alerts!",
            "html": html_content
        })
        return True
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        return False
