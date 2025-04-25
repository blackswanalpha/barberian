from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from .models import Report
from apps.core.models import User, BusinessSettings, BusinessHours, Holiday
from apps.services.models import Category, Service
from apps.staff.models import StaffSettings

class UserForm(UserCreationForm):
    """
    Form for creating a new user.
    """
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'role', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserEditForm(forms.ModelForm):
    """
    Form for editing a user.
    """
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'role', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BusinessSettingsForm(forms.ModelForm):
    """
    Form for editing business settings.
    """
    class Meta:
        model = BusinessSettings
        fields = ['business_name', 'address', 'phone', 'email', 'logo', 'about', 'facebook_url', 'instagram_url', 'twitter_url']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class BusinessHoursForm(forms.ModelForm):
    """
    Form for editing business hours.
    """
    class Meta:
        model = BusinessHours
        fields = ['day_of_week', 'is_open', 'opening_time', 'closing_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_open = cleaned_data.get('is_open')
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')

        if is_open and opening_time and closing_time and opening_time >= closing_time:
            raise forms.ValidationError(_("Closing time must be after opening time."))

        return cleaned_data

class HolidayForm(forms.ModelForm):
    """
    Form for editing holidays.
    """
    class Meta:
        model = Holiday
        fields = ['name', 'date', 'is_recurring']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoryForm(forms.ModelForm):
    """
    Form for editing service categories.
    """
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ServiceForm(forms.ModelForm):
    """
    Form for editing services.
    """
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration', 'category', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ReportForm(forms.ModelForm):
    """
    Form for creating a report.
    """
    class Meta:
        model = Report
        fields = ['name', 'type', 'parameters']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'parameters': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StaffForm(UserCreationForm):
    """
    Form for creating a new staff member.
    """
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text=_("A brief description about the staff member that will be visible to clients.")
    )
    profile_image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False,
        help_text=_("Upload a profile image for the staff member.")
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'profile_image', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'staff'

        if commit:
            user.save()
            # Create or update staff settings
            staff_settings, created = StaffSettings.objects.get_or_create(staff=user)

            # Save bio to user profile
            if self.cleaned_data.get('bio'):
                user.bio = self.cleaned_data.get('bio')
                user.save()

            # Save profile image if provided
            if self.cleaned_data.get('profile_image'):
                user.profile_image = self.cleaned_data.get('profile_image')
                user.save()

        return user

class StaffEditForm(forms.ModelForm):
    """
    Form for editing a staff member.
    """
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text=_("A brief description about the staff member that will be visible to clients.")
    )
    profile_image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False,
        help_text=_("Upload a profile image for the staff member.")
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'profile_image', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['bio'].initial = self.instance.bio

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            # Create or update staff settings
            staff_settings, created = StaffSettings.objects.get_or_create(staff=user)

            # Save bio to user profile
            if self.cleaned_data.get('bio'):
                user.bio = self.cleaned_data.get('bio')
                user.save()

            # Save profile image if provided
            if self.cleaned_data.get('profile_image'):
                user.profile_image = self.cleaned_data.get('profile_image')
                user.save()

        return user
