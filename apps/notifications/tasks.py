from django.utils import timezone
from datetime import timedelta

from apps.appointments.models import Appointment
from apps.notifications.models import Notification
from apps.notifications.email_utils import send_appointment_reminder

def send_appointment_reminders():
    """
    Send appointment reminders for appointments that are scheduled for tomorrow.
    This function should be run once a day, preferably in the evening.
    """
    # Get tomorrow's date
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # Get all confirmed appointments for tomorrow
    appointments = Appointment.objects.filter(
        start_time__date=tomorrow,
        status='confirmed'
    )
    
    # Send reminders for each appointment
    for appointment in appointments:
        # Create a notification
        Notification.objects.create(
            user=appointment.client,
            type='reminder',
            title='Appointment Reminder',
            message=f"Reminder: You have an appointment for {appointment.service.name} with {appointment.staff.get_full_name()} tomorrow at {appointment.start_time.strftime('%I:%M %p')}.",
            related_appointment=appointment
        )
        
        # Send an email reminder
        send_appointment_reminder(appointment)
    
    return len(appointments)

def clean_old_notifications():
    """
    Delete notifications that are older than 30 days.
    This function should be run once a day.
    """
    # Get the date 30 days ago
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Delete old notifications
    old_notifications = Notification.objects.filter(
        created_at__lt=thirty_days_ago
    )
    
    count = old_notifications.count()
    old_notifications.delete()
    
    return count
