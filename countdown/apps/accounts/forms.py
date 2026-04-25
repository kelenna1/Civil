from django import forms
from .models import Organization


class OrganizationLoginForm(forms.Form):
    """Form for logging into an existing organization."""
    name = forms.CharField(
        max_length=100,
        label='Organization Name',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter organization name',
            'autocomplete': 'organization',
        })
    )
    password = forms.CharField(
        max_length=128,
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter password',
            'autocomplete': 'current-password',
        })
    )


class OrganizationCreateForm(forms.ModelForm):
    """Form for creating a new organization with password confirmation."""
    password = forms.CharField(
        max_length=128,
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        })
    )
    confirm_password = forms.CharField(
        max_length=128,
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = Organization
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your organization name',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Organization.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError('An organization with this name already exists.')
        return name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords don't match.")
            if len(password) < 6:
                raise forms.ValidationError("Password must be at least 6 characters.")

        return cleaned_data

    def save(self, commit=True):
        organization = super().save(commit=False)
        organization.set_password(self.cleaned_data['password'])
        if commit:
            organization.save()
        return organization


class OrganizationEditForm(forms.ModelForm):
    """Form for editing organization details."""
    class Meta:
        model = Organization
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Organization.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('An organization with this name already exists.')
        return name
