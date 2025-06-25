from django.contrib import admin
from django.urls import path
from . import views
from .views import create_organization, org_login, dashboard, home, add_birthday, org_logout, import_birthdays, edit_birthday, delete_birthday, edit_organization, delete_organization,  notification_settings, unsubscribe

urlpatterns = [
    path('', home, name='home'),
    path('login/', org_login, name='org_login'),
    path('create/', create_organization, name='create_organization'),
    path('dashboard/', dashboard, name='dashboard'),
    path('add/', add_birthday, name='add_birthday'),
    path('logout/', org_logout, name='org_logout'),
    path('import/', import_birthdays, name='import_birthdays'),
    path('birthday/edit/<int:birthday_id>/', edit_birthday, name='edit_birthday'),
    path('birthday/delete/<int:birthday_id>/', delete_birthday, name='delete_birthday'),
    path('organization/edit/', edit_organization, name='edit_organization'),
    path('organization/delete/', delete_organization, name='delete_organization'),
    path('notifications/', notification_settings, name='notification_settings'),
    path('unsubscribe/<uuid:token>/', unsubscribe, name='unsubscribe'),
]


handler404 = views.custom_page_not_found_view
handler500 = views.custom_error_view
handler403 = views.custom_permission_denied_view
handler400 = views.custom_bad_request_view