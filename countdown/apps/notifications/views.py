from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from apps.accounts.decorators import org_login_required
from .models import NotificationSubscription
from .services import send_welcome_email


@org_login_required
def notification_settings(request):
    """Subscribe to birthday notifications for the current organization."""
    org = request.organization

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'pages/notifications/settings.html', {
                'organization': org,
                'email_value': email,
            })

        subscription, created = NotificationSubscription.objects.update_or_create(
            organization=org,
            email=email,
            defaults={'is_active': True}
        )

        send_welcome_email(subscription)

        if created:
            messages.success(request, "You're subscribed! Check your email for confirmation.")
        else:
            messages.success(request, "Subscription reactivated! Check your email.")

        return redirect('dashboard')

    # Show existing subscriptions
    subscriptions = NotificationSubscription.objects.filter(
        organization=org,
        is_active=True,
    )

    return render(request, 'pages/notifications/settings.html', {
        'organization': org,
        'subscriptions': subscriptions,
    })


def unsubscribe(request, token):
    """Unsubscribe from notifications via token link."""
    subscription = get_object_or_404(NotificationSubscription, unsubscribe_token=token)
    subscription.is_active = False
    subscription.save(update_fields=['is_active'])

    return render(request, 'pages/notifications/unsubscribed.html', {
        'organization': subscription.organization,
    })
