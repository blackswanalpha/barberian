from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Appointment
from apps.services.models import Service
from apps.core.models import User

class ServiceSelectionForm(forms.Form):
    """
    Form for selecting a service for an appointment.
    """
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        empty_label=_("Select a service"),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Service")
    )

class StaffSelectionForm(forms.Form):
    """
    Form for selecting a staff member for an appointment.
    """
    staff = forms.ModelChoiceField(
        queryset=User.objects.filter(role='staff', is_active=True),
        empty_label=_("Select a staff member"),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Staff Member")
    )

    def __init__(self, *args, **kwargs):
        service_id = kwargs.pop('service_id', None)
        super().__init__(*args, **kwargs)

        if service_id:
            # Filter staff members who can provide the selected service
            # In a real application, you might have a many-to-many relationship between staff and services
            # For now, we'll just show all staff members
            self.fields['staff'].queryset = User.objects.filter(role='staff', is_active=True)

class DateSelectionForm(forms.Form):
    """
    Form for selecting a date for an appointment.
    """
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label=_("Date"),
        initial=timezone.now().date()
    )

    def __init__(self, *args, **kwargs):
        service_id = kwargs.pop('service_id', None)
        super().__init__(*args, **kwargs)

        # Set minimum date to today
        self.fields['date'].widget.attrs['min'] = timezone.now().date().isoformat()

        # Set maximum date to 30 days from now
        max_date = (timezone.now() + timedelta(days=30)).date().isoformat()
        self.fields['date'].widget.attrs['max'] = max_date

    def clean_date(self):
        date = self.cleaned_data['date']
        today = timezone.now().date()

        if date < today:
            raise forms.ValidationError(_("You cannot book an appointment in the past."))

        if date > today + timedelta(days=30):
            raise forms.ValidationError(_("You cannot book an appointment more than 30 days in advance."))

        return date

class TimeSelectionForm(forms.Form):
    """
    Form for selecting a time for an appointment.
    """
    time = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label=_("Select Your Preferred Time")
    )

    def __init__(self, *args, **kwargs):
        service_id = kwargs.pop('service_id', None)
        date = kwargs.pop('date', None)
        super().__init__(*args, **kwargs)

        if service_id and date:
            try:
                # Get the service
                service = Service.objects.get(id=service_id)

                # Generate time slots from 9 AM to 8 PM at 15-minute intervals
                time_slots = []
                current_date = date

                # Check if the date is today
                is_today = current_date == timezone.localtime().date()
                current_hour = timezone.localtime().hour if is_today else 0

                # Business hours (9 AM to 8 PM)
                start_hour = max(9, current_hour + 1) if is_today else 9
                end_hour = 20  # 8 PM

                for hour in range(start_hour, end_hour):
                    for minute in [0, 15, 30, 45]:
                        # Skip times in the past if it's today
                        if is_today and hour == current_hour + 1 and minute < timezone.localtime().minute:
                            continue

                        time_obj = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
                        time_slots.append(time_obj)

                # Store the time slots as a dictionary for easy lookup
                self.time_slots_dict = {slot.strftime('%H:%M'): slot for slot in time_slots}

                # Set the choices for the time field
                self.fields['time'].choices = [(slot.strftime('%H:%M'), slot.strftime('%I:%M %p')) for slot in time_slots]

                print(f"Generated {len(time_slots)} time slots for booking")

            except Exception as e:
                # Log any errors
                print(f"Error generating time slots: {str(e)}")
                self.fields['time'].choices = []
                self.time_slots_dict = {}

    def clean_time(self):
        """
        Clean the time field and convert it to a string in the format 'HH:MM'.
        """
        time_str = self.cleaned_data['time']

        # Validate that the time is in the correct format
        try:
            # Parse the time string to ensure it's valid
            hour, minute = map(int, time_str.split(':'))
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise forms.ValidationError(_("Invalid time format. Please select a valid time."))

            # Return the time string in the format 'HH:MM'
            return time_str
        except ValueError:
            raise forms.ValidationError(_("Invalid time format. Please select a valid time."))

class ConfirmationForm(forms.ModelForm):
    """
    Form for confirming an appointment.
    """
    class Meta:
        model = Appointment
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
