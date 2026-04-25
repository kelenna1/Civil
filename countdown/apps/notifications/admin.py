from django.contrib import admin
from .models import NotificationSubscription


@admin.register(NotificationSubscription)
class NotificationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'organization', 'is_active', 'created_at')
    list_filter = ('is_active', 'organization')
    search_fields = ('email',)
    readonly_fields = ('unsubscribe_token', 'created_at')
