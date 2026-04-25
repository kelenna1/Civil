from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.org_login, name='org_login'),
    path('register/', views.create_organization, name='create_organization'),
    path('logout/', views.org_logout, name='org_logout'),
    path('organization/edit/', views.edit_organization, name='edit_organization'),
    path('organization/delete/', views.delete_organization, name='delete_organization'),
]
