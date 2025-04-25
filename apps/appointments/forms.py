from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta, time

from .models import Appointment
from apps.services.models import Service
from apps.core.models import User
from apps.staff.models import Schedule

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
        staff_id = kwargs.pop('staff_id', None)
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
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Time")
    )
    
    def __init__(self, *args, **kwargs):
        staff_id = kwargs.pop('staff_id', None)
        service_id = kwargs.pop('service_id', None)
        date = kwargs.pop('date', None)
        super().__init__(*args, **kwargs)
        
        if staff_id and service_id and date:
            # Get the staff member's schedule for the selected date
            staff = User.objects.get(id=staff_id)
            service = Service.objects.get(id=service_id)
            
            # Get the day of the week (0 = Monday, 6 = Sunday)
            day_of_week = date.weekday()
            
            # Get the staff member's schedule for this day
            try:
                schedule = Schedule.objects.get(staff=staff, day_of_week=day_of_week, is_working=True)
                
                # Generate time slots based on the schedule and service duration
                time_slots = self._generate_time_slots(schedule.start_time, schedule.end_time, service.duration)
                
                # Filter out time slots that are already booked
                available_slots = self._filter_available_slots(staff, date, time_slots, service.duration)
                
                self.fields['time'].choices = [(slot.strftime('%H:%M'), slot.strftime('%I:%M %p')) for slot in available_slots]
            except Schedule.DoesNotExist:
                # Staff member is not working on this day
                self.fields['time'].choices = []
    
    def _generate_time_slots(self, start_time, end_time, duration):
        """
        Generate time slots based on the schedule and service duration.
        """
        slots = []
        current_time = datetime.combine(timezone.now().date(), start_time)
        end_datetime = datetime.combine(timezone.now().date(), end_time)
        
        # Subtract service duration to ensure the appointment ends before the schedule end time
        end_datetime = end_datetime - timedelta(minutes=duration)
        
        # Generate slots at 15-minute intervals
        while current_time <= end_datetime:
            slots.append(current_time.time())
            current_time += timedelta(minutes=15)
        
        return slots
    
    def _filter_available_slots(self, staff, date, time_slots, duration):
        """
        Filter out time slots that are already booked.
        """
        available_slots = []
        
        for slot in time_slots:
            # Convert the time slot to a datetime
            start_datetime = datetime.combine(date, slot)
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            # Check if there are any overlapping appointments
            overlapping_appointments = Appointment.objects.filter(
                staff=staff,
                start_time__lt=end_datetime,
                end_time__gt=start_datetime,
                status__in=['pending', 'confirmed']
            )
            
            if not overlapping_appointments.exists():
                available_slots.append(slot)
        
        return available_slots

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
