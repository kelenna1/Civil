"""
URL configuration for CandlesDown.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('', include('apps.birthdays.urls')),
    path('', include('apps.notifications.urls')),
]

# Custom error handlers
handler400 = 'apps.accounts.views.custom_bad_request_view'
handler403 = 'apps.accounts.views.custom_permission_denied_view'
handler404 = 'apps.accounts.views.custom_page_not_found_view'
handler500 = 'apps.accounts.views.custom_error_view'