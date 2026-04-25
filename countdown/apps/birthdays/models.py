from django.db import models
from django.db.models.functions import ExtractMonth, ExtractDay
from django.core.validators import FileExtensionValidator
from apps.accounts.models import Organization


class Birthday(models.Model):
    """A person's birthday tracked within an organization."""
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='birthdays'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'birthday_birthday'
        ordering = ['full_name']
        verbose_name_plural = 'birthdays'
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['date_of_birth']),
            models.Index(
                ExtractMonth('date_of_birth'),
                ExtractDay('date_of_birth'),
                name='bday_month_day_idx'
            ),
        ]

    def __str__(self):
        return f"{self.full_name} — {self.date_of_birth.strftime('%b %d')}"


class BirthdayImport(models.Model):
    """Record of a bulk birthday import from a file."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='imports'
    )
    file = models.FileField(
        upload_to='birthday_imports/',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls', 'csv'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    status_detail = models.TextField(blank=True, default='')
    records_added = models.PositiveIntegerField(default=0)
    records_skipped = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'birthday_birthdayimport'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Import for {self.organization.name} ({self.uploaded_at:%Y-%m-%d})"
