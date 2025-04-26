from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserChangeForm
from django.conf import settings

from .models import StaffSettings, Schedule
from apps.core.models import User

class StaffProfileForm(UserChangeForm):
    """
    Form for updating staff profile information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio', 'specialization', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class StaffSettingsForm(forms.ModelForm):
    """
    Form for updating staff settings.
    """
    class Meta:
        model = StaffSettings
        fields = ['notification_preference', 'email_notifications', 'sms_notifications', 'auto_confirm_appointments', 'calendar_view_preference', 'services']
        widgets = {
            'notification_preference': forms.Select(attrs={'class': 'form-select'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_confirm_appointments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'calendar_view_preference': forms.Select(attrs={'class': 'form-select'}),
            'services': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

class ScheduleForm(forms.ModelForm):
    """
    Form for updating staff schedule.
    """
    class Meta:
        model = Schedule
        fields = ['day_of_week', 'start_time', 'end_time', 'is_working']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_working': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        is_working = cleaned_data.get('is_working')

        if is_working and start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(_("End time must be after start time."))

        return cleaned_data
