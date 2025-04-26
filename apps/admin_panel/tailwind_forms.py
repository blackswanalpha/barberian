from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from .models import Report
from apps.core.models import User, BusinessSettings, BusinessHours, Holiday
from apps.services.models import Category, Service
from apps.staff.models import StaffSettings

# Common input classes for Tailwind CSS styling
MATERIAL_INPUT_CLASSES = "block py-2.5 px-0 w-full text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none focus:outline-none focus:ring-0 focus:border-primary-500 pl-10 peer placeholder-transparent"
TEXTAREA_CLASSES = "block p-2.5 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 min-h-[120px]"
SELECT_CLASSES = "block py-2.5 px-0 w-full text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none focus:outline-none focus:ring-0 focus:border-primary-500 pl-10 peer"
CHECKBOX_CLASSES = "sr-only" # For toggle switch
FILE_INPUT_CLASSES = "sr-only" # Hidden but accessible

class ServiceForm(forms.ModelForm):
    """
    Form for editing services with Tailwind CSS styling.
    """
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration', 'category', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Service Name',
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_CLASSES,
                'rows': 3,
                'placeholder': 'Describe the service...',
            }),
            'price': forms.NumberInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'step': '0.01',
                'placeholder': 'Price',
            }),
            'duration': forms.NumberInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Duration',
            }),
            'category': forms.Select(attrs={
                'class': SELECT_CLASSES,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASSES,
            }),
        }

class CategoryForm(forms.ModelForm):
    """
    Form for editing service categories with Tailwind CSS styling.
    """
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Category Name',
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_CLASSES,
                'rows': 3,
                'placeholder': 'Describe the category...',
            }),
            'image': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASSES,
                'accept': 'image/*',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASSES,
            }),
        }

class StaffForm(forms.ModelForm):
    """
    Form for creating a new staff member with Tailwind CSS styling.
    """
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'block p-4 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-400 focus:border-primary-400 min-h-[120px] transition-all duration-200',
            'rows': 3,
            'placeholder': 'Staff bio...',
        }),
        required=False,
        help_text=_("A brief description about the staff member that will be visible to clients.")
    )
    profile_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': FILE_INPUT_CLASSES,
            'accept': 'image/*',
        }),
        required=False,
        help_text=_("Upload a profile image for the staff member.")
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'profile_image', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'block py-3 px-4 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 appearance-none focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 pl-10 transition-all duration-200',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block py-3 px-4 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 appearance-none focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 pl-10 transition-all duration-200',
                'placeholder': 'Last Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block py-3 px-4 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 appearance-none focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 pl-10 transition-all duration-200',
                'placeholder': 'Email Address',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASSES,
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'staff'

        # Generate a random password
        import random
        import string
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        user.set_password(random_password)

        if commit:
            user.save()
            # Create or update staff settings
            # Using _ to ignore the created variable to avoid linting warnings
            _, _ = StaffSettings.objects.get_or_create(staff=user)

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
    Form for editing a staff member with Tailwind CSS styling.
    """
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'block p-4 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-400 focus:border-primary-400 min-h-[120px] transition-all duration-200',
            'rows': 3,
            'placeholder': 'Staff bio...',
        }),
        required=False,
        help_text=_("A brief description about the staff member that will be visible to clients.")
    )
    profile_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': FILE_INPUT_CLASSES,
            'accept': 'image/*',
        }),
        required=False,
        help_text=_("Upload a profile image for the staff member.")
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'profile_image', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'block py-3 px-4 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 appearance-none focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 pl-10 transition-all duration-200',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block py-3 px-4 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 appearance-none focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 pl-10 transition-all duration-200',
                'placeholder': 'Last Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block py-3 px-4 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 appearance-none focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 pl-10 transition-all duration-200',
                'placeholder': 'Email Address',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASSES,
            }),
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
            # Using _ to ignore the created variable to avoid linting warnings
            _, _ = StaffSettings.objects.get_or_create(staff=user)

            # Save bio to user profile
            if self.cleaned_data.get('bio'):
                user.bio = self.cleaned_data.get('bio')
                user.save()

            # Save profile image if provided
            if self.cleaned_data.get('profile_image'):
                user.profile_image = self.cleaned_data.get('profile_image')
                user.save()

        return user

class BusinessSettingsForm(forms.ModelForm):
    """
    Form for editing business settings with Tailwind CSS styling.
    """
    class Meta:
        model = BusinessSettings
        fields = ['business_name', 'address', 'phone', 'email', 'logo', 'about', 'facebook_url', 'instagram_url', 'twitter_url']
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Business Name',
            }),
            'address': forms.Textarea(attrs={
                'class': TEXTAREA_CLASSES,
                'rows': 3,
                'placeholder': 'Business Address',
            }),
            'phone': forms.TextInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Phone Number',
            }),
            'email': forms.EmailInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Email Address',
            }),
            'logo': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASSES,
                'accept': 'image/*',
            }),
            'about': forms.Textarea(attrs={
                'class': TEXTAREA_CLASSES,
                'rows': 5,
                'placeholder': 'About your business...',
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Facebook URL',
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Instagram URL',
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Twitter URL',
            }),
        }

class BusinessHoursForm(forms.ModelForm):
    """
    Form for editing business hours with Tailwind CSS styling.
    """
    class Meta:
        model = BusinessHours
        fields = ['day_of_week', 'is_open', 'opening_time', 'closing_time']
        widgets = {
            'day_of_week': forms.Select(attrs={
                'class': SELECT_CLASSES,
            }),
            'is_open': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASSES,
            }),
            'opening_time': forms.TimeInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'type': 'time',
            }),
            'closing_time': forms.TimeInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'type': 'time',
            }),
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
    Form for editing holidays with Tailwind CSS styling.
    """
    class Meta:
        model = Holiday
        fields = ['name', 'date', 'is_recurring']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Holiday Name',
            }),
            'date': forms.DateInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'type': 'date',
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASSES,
            }),
        }

class ReportForm(forms.ModelForm):
    """
    Form for creating a report with Tailwind CSS styling.
    """
    class Meta:
        model = Report
        fields = ['name', 'type', 'parameters']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': MATERIAL_INPUT_CLASSES,
                'placeholder': 'Report Name',
            }),
            'type': forms.Select(attrs={
                'class': SELECT_CLASSES,
            }),
            'parameters': forms.Textarea(attrs={
                'class': TEXTAREA_CLASSES,
                'rows': 3,
                'placeholder': 'Report Parameters (JSON)',
            }),
        }
