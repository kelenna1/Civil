from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError


class Organization(models.Model):
    """
    Represents an organization that tracks birthdays.
    Uses its own password-based authentication (not Django's User model).
    """
    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'birthday_organization'
        ordering = ['name']

    def clean(self):
        if Organization.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': 'An organization with this name already exists.'})

    def set_password(self, raw_password):
        """Hash and store the password."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify a raw password against the stored hash."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name
