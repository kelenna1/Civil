from django import forms
from .models import Organization, Birthday, BirthdayImport
from django.contrib.auth.hashers import make_password

class OrganizationLoginForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Organization Name',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    password = forms.CharField(
        max_length=100,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

class OrganizationCreateForm(forms.ModelForm):
    password = forms.CharField(
        max_length=100,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )
    confirm_password = forms.CharField(
        max_length=100,
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Organization
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if Organization.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("An organization with this name already exists.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        organization = super().save(commit=False)
        organization.set_password(self.cleaned_data['password'])
        if commit:
            organization.save()
        return organization

class BirthdayForm(forms.ModelForm):
    class Meta:
        model = Birthday
        fields = ['full_name', 'date_of_birth']

class BirthdayImportForm(forms.ModelForm):
    class Meta:
        model = BirthdayImport
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': '.xlsx,.xls,.csv',
                'class': 'file-input'
            })
        }


class OrganizationEditForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name']