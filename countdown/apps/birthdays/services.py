"""
Birthday calculation service — the SINGLE source of truth for all
countdown logic in the application. Used by views, templates, and
the notification management command.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from django.db.models import Case, When, Value, BooleanField, Q
from django.db.models.functions import ExtractMonth, ExtractDay


@dataclass
class CountdownResult:
    """Result of a birthday countdown calculation."""
    next_birthday: date
    days: int
    hours: int
    minutes: int
    seconds: int
    turning_age: int
    is_today: bool

    @property
    def total_seconds(self):
        return self.days * 86400 + self.hours * 3600 + self.minutes * 60 + self.seconds


def calculate_countdown(birth_date: date, reference: Optional[datetime] = None) -> CountdownResult:
    """
    Calculate the countdown to someone's next birthday.
    
    Handles edge cases:
    - Leap year birthdays (Feb 29): if this year isn't a leap year,
      the birthday is celebrated on Feb 28.
    - Birthday is today: is_today=True, countdown shows 0.
    - Birthday has passed this year: calculates for next year.
    
    Args:
        birth_date: The person's date of birth.
        reference: The reference datetime (defaults to now).
    
    Returns:
        CountdownResult with all countdown fields.
    """
    if reference is None:
        reference = datetime.now()

    today = reference.date() if isinstance(reference, datetime) else reference
    now = reference if isinstance(reference, datetime) else datetime.combine(reference, datetime.min.time())

    # Calculate this year's birthday, handling Feb 29
    next_birthday = _get_birthday_in_year(birth_date, today.year)

    if next_birthday < today:
        # Birthday has passed this year, calculate for next year
        next_birthday = _get_birthday_in_year(birth_date, today.year + 1)

    # Calculate turning age
    turning_age = next_birthday.year - birth_date.year

    # Check if birthday is today
    is_today = next_birthday == today

    if is_today:
        return CountdownResult(
            next_birthday=next_birthday,
            days=0,
            hours=0,
            minutes=0,
            seconds=0,
            turning_age=turning_age,
            is_today=True,
        )

    # Calculate precise countdown to midnight of the birthday
    target = datetime.combine(next_birthday, datetime.min.time())
    delta = target - now
    total_seconds = int(delta.total_seconds())

    days = total_seconds // 86400
    remaining = total_seconds % 86400
    hours = remaining // 3600
    remaining = remaining % 3600
    minutes = remaining // 60
    seconds = remaining % 60

    return CountdownResult(
        next_birthday=next_birthday,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        turning_age=turning_age,
        is_today=False,
    )


def _get_birthday_in_year(birth_date: date, year: int) -> date:
    """
    Get the birthday date in a specific year.
    Handles Feb 29 → Feb 28 for non-leap years.
    """
    try:
        return birth_date.replace(year=year)
    except ValueError:
        # Feb 29 in a non-leap year → Feb 28
        return date(year, 2, 28)


def get_annotated_birthdays_qs(birthdays_qs):
    """
    Annotates a Birthday queryset with month, day, and a boolean indicating
    if the birthday is coming up this year or next year, and sorts it.
    
    This replaces the expensive in-memory Python sorting with fast database SQL sorting.
    """
    today = date.today()
    current_month = today.month
    current_day = today.day

    # Annotate month and day
    qs = birthdays_qs.annotate(
        bmonth=ExtractMonth('date_of_birth'),
        bday=ExtractDay('date_of_birth'),
    )

    # Annotate if the birthday is happening THIS year (True) or NEXT year (False)
    # A birthday is this year if its month is > current month, 
    # OR if its month is == current month AND its day >= current day.
    qs = qs.annotate(
        is_this_year=Case(
            When(
                Q(bmonth__gt=current_month) | Q(bmonth=current_month, bday__gte=current_day),
                then=Value(True)
            ),
            default=Value(False),
            output_field=BooleanField(),
        )
    )

    # Sort:
    # 1. is_this_year DESC (True first, False second)
    # 2. bmonth ASC
    # 3. bday ASC
    return qs.order_by('-is_this_year', 'bmonth', 'bday')


def process_page_birthdays(page_obj):
    """
    Attach the `calculate_countdown` result directly to the model instances
    for a paginated subset of birthdays.
    """
    for birthday in page_obj:
        countdown = calculate_countdown(birthday.date_of_birth)
        # Attach properties dynamically to the model instance for the template
        birthday.countdown = countdown
        birthday.next_birthday = countdown.next_birthday
        birthday.turning = countdown.turning_age
        birthday.is_today = countdown.is_today
    
    return page_obj
