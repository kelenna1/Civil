from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from apps.accounts.decorators import org_login_required
from .models import Birthday, BirthdayImport
from .forms import BirthdayForm, BirthdayImportForm
from .services import get_annotated_birthdays_qs, process_page_birthdays, calculate_countdown
from .utils import process_birthday_import


@org_login_required
def dashboard(request):
    """Main dashboard with birthday countdowns."""
    org = request.organization
    birthdays_qs = org.birthdays.filter(is_active=True)

    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        birthdays_qs = birthdays_qs.filter(full_name__icontains=search_query)

    # Database-level sorting (Replaces massive in-memory evaluation)
    annotated_qs = get_annotated_birthdays_qs(birthdays_qs)

    from datetime import date
    import calendar as cal_mod
    today = date.today()
    current_month = today.month
    current_year = today.year
    current_day = today.day

    # Stats - direct DB counts
    total_count = birthdays_qs.count()
    
    today_qs = org.birthdays.filter(
        is_active=True,
        date_of_birth__month=current_month,
        date_of_birth__day=current_day
    )
    today_count = today_qs.count()

    this_month_qs = org.birthdays.filter(
        is_active=True,
        date_of_birth__month=current_month,
    )
    this_month_count = this_month_qs.count()

    # Build today's celebrants list for modal
    today_birthdays = process_page_birthdays(list(today_qs))

    # Build this-month calendar data for modal
    month_days = {}
    for bday in this_month_qs:
        day = bday.date_of_birth.day
        if day not in month_days:
            month_days[day] = []
        month_days[day].append(bday.full_name)

    # Calendar metadata
    first_weekday, num_days = cal_mod.monthrange(current_year, current_month)
    month_name = today.strftime('%B %Y')

    # Pagination directly on the database QuerySet
    page_number = request.GET.get('page', 1)
    paginator = Paginator(annotated_qs, 20)
    page_obj = paginator.get_page(page_number)
    
    # Process only the 20 items for the current page
    processed_page = process_page_birthdays(page_obj.object_list)
    page_obj.object_list = processed_page

    # Next birthday (the soonest upcoming one)
    next_birthday = None
    first_bday = annotated_qs.first()
    if first_bday:
        next_birthday = process_page_birthdays([first_bday])[0]

    context = {
        'organization': org,
        'birthdays': page_obj,
        'next_birthday': next_birthday,
        'search_query': search_query,
        'stats': {
            'total': total_count,
            'today': today_count,
            'this_month': this_month_count,
        },
        'today_birthdays': today_birthdays,
        'month_name': month_name,
        'month_days': month_days,
        'month_num_days': num_days,
        'month_first_weekday': first_weekday,
        'today_day': today.day,
    }
    return render(request, 'pages/dashboard.html', context)


@org_login_required
def add_birthday(request):
    """Add a single birthday."""
    if request.method == 'POST':
        form = BirthdayForm(request.POST)
        if form.is_valid():
            birthday = form.save(commit=False)
            birthday.organization = request.organization
            birthday.save()
            messages.success(request, f"Added {birthday.full_name}'s birthday!")
            return redirect('dashboard')
    else:
        form = BirthdayForm()

    return render(request, 'pages/birthdays/add.html', {
        'form': form,
        'organization': request.organization,
    })


@org_login_required
def edit_birthday(request, birthday_id):
    """Edit an existing birthday."""
    birthday = get_object_or_404(
        Birthday,
        id=birthday_id,
        organization=request.organization,
        is_active=True,
    )

    if request.method == 'POST':
        form = BirthdayForm(request.POST, instance=birthday)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {birthday.full_name}'s birthday!")
            return redirect('dashboard')
    else:
        form = BirthdayForm(instance=birthday)

    return render(request, 'pages/birthdays/edit.html', {
        'form': form,
        'birthday': birthday,
    })


@org_login_required
@require_POST
def delete_birthday(request, birthday_id):
    """
    Soft-delete a birthday.
    Requires POST to prevent accidental/malicious deletion via GET.
    """
    birthday = get_object_or_404(
        Birthday,
        id=birthday_id,
        organization=request.organization,
        is_active=True,
    )
    birthday.is_active = False
    birthday.save(update_fields=['is_active'])
    messages.success(request, f"Removed {birthday.full_name}'s birthday.")
    return redirect('dashboard')


@org_login_required
def import_birthdays(request):
    """Import birthdays from an Excel or CSV file."""
    if request.method == 'POST':
        form = BirthdayImportForm(request.POST, request.FILES)
        if form.is_valid():
            import_obj = form.save(commit=False)
            import_obj.organization = request.organization
            import_obj.status = 'processing'
            import_obj.save()

            result = process_birthday_import(import_obj)

            if result.is_success:
                msg = f"Successfully imported {result.added} birthday"
                if result.added != 1:
                    msg += "s"
                if result.skipped:
                    msg += f" ({result.skipped} duplicates skipped)"
                messages.success(request, msg + "!")
            else:
                error_summary = "; ".join(result.errors[:3])
                if len(result.errors) > 3:
                    error_summary += f" ... and {len(result.errors) - 3} more errors"
                messages.error(request, f"Import had issues: {error_summary}")
                if result.added:
                    messages.info(request, f"{result.added} records were still imported successfully.")

            return redirect('dashboard')
    else:
        form = BirthdayImportForm()

    return render(request, 'pages/birthdays/import.html', {
        'form': form,
        'organization': request.organization,
    })
