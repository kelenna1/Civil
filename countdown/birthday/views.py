from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from datetime import datetime, timedelta
import pandas as pd
from .models import Organization, Birthday, BirthdayImport, NotificationSubscription
from .forms import (
    OrganizationLoginForm, 
    OrganizationCreateForm, 
    BirthdayForm, 
    BirthdayImportForm, 
    OrganizationEditForm,
    NotificationSubscriptionForm
)
from .services import send_birthday_notification, send_welcome_email



def home(request):  
    return render(request, 'birthday/home.html')


def org_login(request):
    error = None
    if request.method == 'POST':
        form = OrganizationLoginForm(request.POST)
        if form.is_valid():
            org_name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            try:
                org = Organization.objects.get(name=org_name)
                if org.check_password(password):
                    request.session['org_id'] = org.id
                    messages.success(request, "Logged in successfully!")
                    return redirect('dashboard')
                else:
                    error = "Invalid password"
            except Organization.DoesNotExist:
                error = "Organization does not exist"
    else:
        form = OrganizationLoginForm()
    return render(request, 'birthday/org_login.html', {'form': form, 'error': error})


def dashboard(request):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')
    
    try:
        org = Organization.objects.get(id=org_id)
        birthdays = org.birthdays.filter(is_active=True)
        upcoming_birthdays = get_upcoming_birthdays(birthdays)
        
        next_birthday = None
        if upcoming_birthdays:
            next_birthday = upcoming_birthdays[0]
            if isinstance(next_birthday, dict) and 'id' not in next_birthday:
                next_birthday = None
        
        context = {
            'organization': org,
            'birthdays': upcoming_birthdays,
            'next_birthday': next_birthday
        }
        return render(request, 'birthday/dashboard.html', context)
        
    except Organization.DoesNotExist:
        return HttpResponseForbidden("Organization not found")


def create_organization(request):
    if request.method == 'POST':
        form = OrganizationCreateForm(request.POST)
        if form.is_valid():
            try:
                org = form.save()
                request.session['org_id'] = org.id
                messages.success(request, "Organization created successfully!")
                return redirect('dashboard')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = OrganizationCreateForm()

    return render(request, 'birthday/create_organization.html', {
        'form': form,
        'errors': form.errors if form.errors else None
    })


def org_logout(request):
    try:
        del request.session['org_id']
        messages.success(request, "Logged out successfully!")
    except KeyError:
        pass
    return redirect('org_login')


def calculate_next_birthday(birth_date):
    today = datetime.today().date()
    this_year_birthday = birth_date.replace(year=today.year)

    if this_year_birthday < today:
        next_birthday = this_year_birthday.replace(year=today.year + 1)
    else:
        next_birthday = this_year_birthday

    delta = next_birthday - today
    return {
        'date': next_birthday,
        'days': delta.days,
        'hours': 0,
        'minutes': 0,
        'seconds': 0
    }


def get_upcoming_birthdays(birthdays):
    today = datetime.today().date()
    upcoming = []
    
    for b in birthdays:
        birth_date = b.date_of_birth
        next_birthday = birth_date.replace(year=today.year)
        
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        
        delta = next_birthday - today
        total_seconds = delta.total_seconds()
        
        days = delta.days
        hours = int((total_seconds // 3600) % 24)
        minutes = int((total_seconds // 60) % 60)
        seconds = int(total_seconds % 60)
        
        upcoming.append({
            'id': b.id,
            'full_name': b.full_name,
            'birth_date': birth_date,
            'next_birthday': next_birthday,
            'countdown': {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            },
            'turning': (today.year - birth_date.year) + (1 if (today.month, today.day) < (birth_date.month, birth_date.day) else 0)
        })
    
    return sorted(upcoming, key=lambda x: x['countdown']['days'])


def add_birthday(request):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    if request.method == 'POST':
        form = BirthdayForm(request.POST)
        if form.is_valid():
            birthday = form.save(commit=False)
            birthday.organization_id = org_id
            birthday.save()
            messages.success(request, "Birthday added successfully!")
            return redirect('dashboard')
    else:
        form = BirthdayForm()

    return render(request, 'birthday/add_birthday.html', {'form': form})


def import_birthdays(request):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    if request.method == 'POST':
        form = BirthdayImportForm(request.POST, request.FILES)
        if form.is_valid():
            import_obj = form.save(commit=False)
            import_obj.organization_id = org_id
            import_obj.status = "processing"
            import_obj.save()
            
            try:
                if import_obj.file.name.endswith('.csv'):
                    df = pd.read_csv(import_obj.file)
                else:
                    df = pd.read_excel(import_obj.file)
                
                required_columns = {'name', 'date_of_birth'}
                if not required_columns.issubset(df.columns):
                    raise ValueError("File must contain 'name' and 'date_of_birth' columns")
                
                df['name'] = df['name'].str[:100]
                
                birthdays = []
                for _, row in df.iterrows():
                    birthdays.append(Birthday(
                        full_name=row['name'],
                        date_of_birth=row['date_of_birth'],
                        organization_id=org_id
                    ))
                
                Birthday.objects.bulk_create(birthdays)
                import_obj.status = 'success'
                import_obj.processed = True
                import_obj.save()
                
                messages.success(request, f"Successfully imported {len(birthdays)} birthdays!")
                return redirect('dashboard')
                
            except Exception as e:
                error_msg = str(e)
                import_obj.status = f'error: {error_msg[:95]}'
                import_obj.save()
                messages.error(request, f"Import failed: {error_msg}")
                form.add_error('file', error_msg)
    else:
        form = BirthdayImportForm()

    return render(request, 'birthday/import_birthdays.html', {
        'form': form,
        'organization': Organization.objects.get(id=org_id)
    })


def edit_birthday(request, birthday_id):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    birthday = get_object_or_404(Birthday, id=birthday_id, organization_id=org_id)
    
    if request.method == 'POST':
        form = BirthdayForm(request.POST, instance=birthday)
        if form.is_valid():
            form.save()
            messages.success(request, "Birthday updated successfully!")
            return redirect('dashboard')
    else:
        form = BirthdayForm(instance=birthday)

    return render(request, 'birthday/edit_birthday.html', {
        'form': form,
        'birthday': birthday
    })


def delete_birthday(request, birthday_id):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    birthday = get_object_or_404(Birthday, id=birthday_id, organization_id=org_id)
    birthday.is_active = False
    birthday.save()
    messages.success(request, "Birthday deleted successfully!")
    return redirect('dashboard')


def edit_organization(request):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    org = get_object_or_404(Organization, id=org_id)
    
    if request.method == 'POST':
        form = OrganizationEditForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            messages.success(request, "Organization details updated successfully!")
            return redirect('dashboard')
    else:
        form = OrganizationEditForm(instance=org)

    return render(request, 'birthday/edit_organization.html', {
        'form': form,
        'organization': org
    })


def delete_organization(request):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    org = get_object_or_404(Organization, id=org_id)

    with transaction.atomic():
        Birthday.objects.filter(organization=org).delete()
        BirthdayImport.objects.filter(organization=org).delete()
        org.delete()

    request.session.pop('org_id', None)
    messages.success(request, "Organization deleted successfully!")
    return redirect('home')


def notification_settings(request):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')
    
    org = get_object_or_404(Organization, id=org_id)
    
    if request.method == 'POST':
        form = NotificationSubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            
            subscription, created = NotificationSubscription.objects.update_or_create(
                organization=org,
                email=email,
                defaults={'is_active': True}
            )
            
            send_welcome_email(subscription)
            
            messages.success(request, "You're subscribed! Check your email for confirmation.")
            return redirect('dashboard')
    else:
        form = NotificationSubscriptionForm()
    
    return render(request, 'birthday/notification_settings.html', {
        'form': form,
        'organization': org
    })


def unsubscribe(request, token):
    subscription = get_object_or_404(NotificationSubscription, unsubscribe_token=token)
    subscription.is_active = False
    subscription.save()
    messages.success(request, "You've been unsubscribed from notifications.")
    return render(request, 'birthday/dashboard.html')


def custom_error_view(request, exception=None):
    return render(request, 'birthday/500.html', status=500)

def custom_page_not_found_view(request, exception):
    return render(request, 'birthday/404.html', status=404)

def custom_permission_denied_view(request, exception):
    return render(request, 'birthday/403.html', status=403)

def custom_bad_request_view(request, exception):
    return render(request, 'birthday/400.html', status=400)