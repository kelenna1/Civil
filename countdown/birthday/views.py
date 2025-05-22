from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden
from .models import Organization, Birthday, BirthdayImport
from .forms import OrganizationLoginForm, OrganizationCreateForm, BirthdayForm, BirthdayImportForm, OrganizationEditForm
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
import pandas as pd
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
                    request.session['org_id'] = org.id  # ✅ FIXED: no more login(request, org)
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
        
        # Ensure we're passing a birthday object with an ID
        next_birthday = None
        if upcoming_birthdays:
            next_birthday = upcoming_birthdays[0]
            # If we're using a dictionary, make sure it has an 'id' key
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
                return redirect('dashboard')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = OrganizationCreateForm()

    return render(request, 'birthday/create_organization.html', {
        'form': form,
        'errors': form.errors if form.errors else None
    })

# def org_logout(request):
#     # Clear the organization session
#     if 'org_id' in request.session:
#         del request.session['org_id']


def org_logout(request):
    try:
        del request.session['org_id']
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
        'hours': 0,  # optional: can enhance with JS for live clock
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
            'id': b.id,  # Add this line to include the birthday ID
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
            import_obj.save()
            
            try:
                # Process the file
                if import_obj.file.name.endswith('.csv'):
                    df = pd.read_csv(import_obj.file)
                else:  # Excel file
                    df = pd.read_excel(import_obj.file)
                
                # Validate and process data
                required_columns = {'name', 'date_of_birth'}
                if not required_columns.issubset(df.columns):
                    raise ValueError("File must contain 'name' and 'date_of_birth' columns")
                
                # Create birthdays
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
                
                return redirect('dashboard')
                
            except Exception as e:
                import_obj.status = f'error: {str(e)}'
                import_obj.save()
                form.add_error('file', str(e))
    else:
        form = BirthdayImportForm()

    return render(request, 'birthday/import_birthdays.html', {
        'form': form,
        'organization': Organization.objects.get(id=org_id)
    })
    
from django.shortcuts import get_object_or_404

# Edit Birthday
def edit_birthday(request, birthday_id):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    birthday = get_object_or_404(Birthday, id=birthday_id, organization_id=org_id)
    
    if request.method == 'POST':
        form = BirthdayForm(request.POST, instance=birthday)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BirthdayForm(instance=birthday)

    return render(request, 'birthday/edit_birthday.html', {
        'form': form,
        'birthday': birthday
    })

# Delete Birthday (soft delete)
def delete_birthday(request, birthday_id):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    birthday = get_object_or_404(Birthday, id=birthday_id, organization_id=org_id)
    birthday.is_active = False
    birthday.save()
    return redirect('dashboard')

# Edit Organization
def edit_organization(request):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    org = get_object_or_404(Organization, id=org_id)
    
    if request.method == 'POST':
        form = OrganizationEditForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = OrganizationEditForm(instance=org)

    return render(request, 'birthday/edit_organization.html', {
        'form': form,
        'organization': org
    })

# Delete Organization (soft delete)
def delete_organization(request):
    org_id = request.session.get('org_id')
    if not org_id:
        return redirect('org_login')

    org = get_object_or_404(Organization, id=org_id)

    # Optional: Cascade delete related birthdays & imports using transaction
    with transaction.atomic():
        # Delete related data manually if not using on_delete=CASCADE in models
        Birthday.objects.filter(organization=org).delete()
        BirthdayImport.objects.filter(organization=org).delete()
        org.delete()  # 🚨 Hard delete from database

    # Clear session
    request.session.pop('org_id', None)

    return redirect('home')