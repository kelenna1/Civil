from django.db import models
from apps.accounts.models import Organization
import uuid


class NotificationSubscription(models.Model):
    """Email subscription for birthday notifications within an organization."""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='notification_subscriptions'
    )
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        db_table = 'birthday_notificationsubscription'
        unique_together = ('organization', 'email')
        verbose_name = 'Email Subscription'
        verbose_name_plural = 'Email Subscriptions'

    def __str__(self):
        status = 'active' if self.is_active else 'inactive'
        return f"{self.email} ({status}) — {self.organization.name}"
