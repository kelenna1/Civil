from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('birthdays/add/', views.add_birthday, name='add_birthday'),
    path('birthdays/<int:birthday_id>/edit/', views.edit_birthday, name='edit_birthday'),
    path('birthdays/<int:birthday_id>/delete/', views.delete_birthday, name='delete_birthday'),
    path('birthdays/import/', views.import_birthdays, name='import_birthdays'),
]
