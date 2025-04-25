from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from apps.core.models import User

class ClientRegistrationForm(UserCreationForm):
    """
    Form for client registration.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

        # Custom labels
        self.fields['password1'].label = _('Password')
        self.fields['password2'].label = _('Confirm Password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Use email as username
        user.role = 'client'  # Set role to client

        if commit:
            user.save()

        return user

class ClientProfileForm(forms.ModelForm):
    """
    Form for updating client profile information.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'profile_image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Custom labels
        self.fields['first_name'].label = _('First Name')
        self.fields['last_name'].label = _('Last Name')
        self.fields['phone_number'].label = _('Phone Number')
        self.fields['profile_image'].label = _('Profile Image')

class ClientPasswordChangeForm(PasswordChangeForm):
    """
    Form for changing client password.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
