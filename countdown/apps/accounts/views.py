from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Organization
from .forms import OrganizationLoginForm, OrganizationCreateForm, OrganizationEditForm
from .decorators import org_login_required


def home(request):
    """Landing page."""
    if request.organization:
        return redirect('dashboard')
    return render(request, 'pages/home.html')


def org_login(request):
    """Organization login."""
    if request.organization:
        return redirect('dashboard')

    error = None
    if request.method == 'POST':
        form = OrganizationLoginForm(request.POST)
        if form.is_valid():
            org_name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            try:
                org = Organization.objects.get(name__iexact=org_name, is_active=True)
                if org.check_password(password):
                    request.session['org_id'] = org.id
                    messages.success(request, f'Welcome back, {org.name}!')
                    return redirect('dashboard')
                else:
                    error = 'Invalid password.'
            except Organization.DoesNotExist:
                error = 'Organization not found.'
    else:
        form = OrganizationLoginForm()

    return render(request, 'pages/auth/login.html', {
        'form': form,
        'error': error,
    })


def create_organization(request):
    """Create a new organization and log in immediately."""
    if request.organization:
        return redirect('dashboard')

    if request.method == 'POST':
        form = OrganizationCreateForm(request.POST)
        if form.is_valid():
            org = form.save()
            request.session['org_id'] = org.id
            messages.success(request, f'{org.name} created successfully! Welcome aboard.')
            return redirect('dashboard')
    else:
        form = OrganizationCreateForm()

    return render(request, 'pages/auth/register.html', {
        'form': form,
    })


def org_logout(request):
    """Log out of the current organization."""
    request.session.pop('org_id', None)
    messages.success(request, 'Logged out successfully.')
    return redirect('org_login')


@org_login_required
def edit_organization(request):
    """Edit organization details."""
    org = request.organization

    if request.method == 'POST':
        form = OrganizationEditForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organization updated successfully!')
            return redirect('dashboard')
    else:
        form = OrganizationEditForm(instance=org)

    return render(request, 'pages/auth/edit_organization.html', {
        'form': form,
        'organization': org,
    })


@org_login_required
@require_POST
def delete_organization(request):
    """
    Delete organization and all associated data.
    Now requires POST (not GET) to prevent accidental/malicious deletion.
    """
    org = request.organization

    # Delete all related data, then the org itself
    from apps.birthdays.models import Birthday, BirthdayImport
    from apps.notifications.models import NotificationSubscription

    Birthday.objects.filter(organization=org).delete()
    BirthdayImport.objects.filter(organization=org).delete()
    NotificationSubscription.objects.filter(organization=org).delete()
    org.delete()

    request.session.pop('org_id', None)
    messages.success(request, 'Organization deleted successfully.')
    return redirect('home')


# =============================================================================
# Custom Error Views
# =============================================================================

def custom_bad_request_view(request, exception):
    return render(request, 'errors/400.html', status=400)


def custom_permission_denied_view(request, exception):
    return render(request, 'errors/403.html', status=403)


def custom_page_not_found_view(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_error_view(request):
    """500 handler — Django calls this without an exception argument."""
    return render(request, 'errors/500.html', status=500)
