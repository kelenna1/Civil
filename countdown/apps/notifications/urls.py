from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notification_settings, name='notification_settings'),
    path('unsubscribe/<uuid:token>/', views.unsubscribe, name='unsubscribe'),
]
