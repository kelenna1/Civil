from django import forms
from .models import Birthday, BirthdayImport


class BirthdayForm(forms.ModelForm):
    """Form for adding/editing a single birthday."""
    class Meta:
        model = Birthday
        fields = ['full_name', 'date_of_birth']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter full name',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
        }
        labels = {
            'full_name': 'Full Name',
            'date_of_birth': 'Date of Birth',
        }


class BirthdayImportForm(forms.ModelForm):
    """Form for uploading a birthday import file."""
    class Meta:
        model = BirthdayImport
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': '.xlsx,.xls,.csv',
                'class': 'file-input',
            })
        }

    def clean_file(self):
        file = self.cleaned_data['file']
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size > max_size:
            raise forms.ValidationError(
                f"File is too large ({file.size // (1024*1024)}MB). Maximum size is 5MB."
            )
        return file
