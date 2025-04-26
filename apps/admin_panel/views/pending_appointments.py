from datetime import datetime, timedelta, time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.appointments.models import Appointment, Service
from apps.core.models import User
from apps.services.models import Service

@login_required
def admin_pending_appointments(request):
    """
    View for admins to see all pending appointment requests.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all pending review appointments
    pending_appointments = Appointment.objects.filter(
        status='pending_review'
    ).order_by('start_time')
    
    # Get today's date for highlighting
    today = timezone.localtime().date()
    tomorrow = today + timedelta(days=1)
    
    # Get today's pending count
    today_count = pending_appointments.filter(start_time__date=today).count()
    
    # Get oldest request date
    oldest_request = None
    if pending_appointments.exists():
        oldest_request = pending_appointments.first().start_time.date()
    
    # Get all services for filtering
    services = Service.objects.all().order_by('name')

    return render(request, 'admin_panel/appointments/pending_list_tailwind.html', {
        'appointments': pending_appointments,
        'title': 'Pending Appointment Requests',
        'today': today,
        'tomorrow': tomorrow,
        'today_count': today_count,
        'oldest_request': oldest_request,
        'services': services,
    })

@login_required
def admin_review_appointment(request, appointment_id):
    """
    View for admins to review and assign staff to an appointment request.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Only allow reviewing pending_review appointments
    if appointment.status != 'pending_review':
        messages.error(request, "This appointment is not pending review.")
        return redirect('admin_panel:appointments')

    # Get today's date for highlighting
    today = timezone.localtime().date()
    tomorrow = today + timedelta(days=1)

    # Handle form submission
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        new_time = request.POST.get('new_time')
        
        if not staff_id:
            messages.error(request, "Please select a staff member.")
            return redirect('admin_panel:review_appointment', appointment_id=appointment_id)
        
        # Get the staff member
        staff = get_object_or_404(User, id=staff_id, role='staff')
        
        # Update the appointment
        appointment.staff = staff
        
        # Update the time if provided
        if new_time:
            current_date = appointment.start_time.date()
            hour, minute = map(int, new_time.split(':'))
            new_datetime = datetime.combine(current_date, time(hour, minute))
            appointment.start_time = new_datetime
        
        # Update the status
        appointment.status = 'confirmed'
        appointment.save()
        
        # Send notifications (would be implemented in a real system)
        # send_appointment_confirmation_email(appointment)
        
        messages.success(request, f"Appointment confirmed and assigned to {staff.get_full_name()}.")
        return redirect('admin_panel:pending_appointments')

    # Get available staff members
    # In a real system, this would check staff availability based on the appointment time
    # For now, we'll just get all staff members
    all_staff = User.objects.filter(role='staff').order_by('first_name')
    
    # Add appointment counts for each staff member
    for staff in all_staff:
        staff.appointments_today = Appointment.objects.filter(
            staff=staff,
            start_time__date=appointment.start_time.date()
        ).count()
    
    # For demo purposes, let's assume some staff are available and some are not
    # In a real system, this would be determined by checking schedules
    available_staff = [staff for staff in all_staff if staff.id % 2 == 0]  # Just an example
    
    # Get appointments for the day to show in the calendar
    day_appointments = Appointment.objects.filter(
        start_time__date=appointment.start_time.date()
    ).exclude(id=appointment_id).order_by('start_time')
    
    # Format appointments for the timeline
    formatted_appointments = []
    for appt in day_appointments:
        # Calculate position in the timeline (assuming 8am-8pm, 12 hours)
        start_hour = appt.start_time.hour
        start_minute = appt.start_time.minute
        duration = appt.service.duration
        
        # Calculate top position (1 hour = 64px)
        top = (start_hour - 8) * 64 + (start_minute / 60) * 64
        height = (duration / 60) * 64
        
        # Assign a color based on status
        if appt.status == 'confirmed':
            color = 'green'
        elif appt.status == 'completed':
            color = 'blue'
        elif appt.status == 'cancelled':
            color = 'red'
        else:
            color = 'gray'
        
        formatted_appointments.append({
            'id': appt.id,
            'client': appt.client,
            'service': appt.service,
            'start_time': appt.start_time,
            'top': top,
            'height': height,
            'color': color
        })
    
    # Calculate position for the current appointment
    appointment_hour = appointment.start_time.hour
    appointment_minute = appointment.start_time.minute
    appointment_duration = appointment.service.duration
    appointment_top = (appointment_hour - 8) * 64 + (appointment_minute / 60) * 64
    appointment_height = (appointment_duration / 60) * 64
    
    # Generate hours for the timeline (8am-8pm)
    hours = range(8, 21)

    return render(request, 'admin_panel/appointments/review_tailwind.html', {
        'title': 'Review Appointment Request',
        'appointment': appointment,
        'all_staff': all_staff,
        'available_staff': available_staff,
        'today': today,
        'tomorrow': tomorrow,
        'day_appointments': formatted_appointments,
        'appointment_top': appointment_top,
        'appointment_height': appointment_height,
        'hours': hours,
    })
