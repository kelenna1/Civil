from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Add unique=True
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Soft delete field

    def clean(self):
        # Check for existing organizations with same name (case-insensitive)
        if Organization.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError('An organization with this name already exists.')

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.name
    
class Birthday(models.Model):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='birthdays')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Soft delete field

    def __str__(self):
        return f"{self.full_name} - {self.date_of_birth}"
    

class BirthdayImport(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    file = models.FileField(upload_to='birthday_imports/',
                          validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls', 'csv'])])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, default='pending')  # 'pending', 'success', 'error'
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Import for {self.organization.name} ({self.uploaded_at})"
        