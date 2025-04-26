from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from datetime import datetime, timedelta

from .models import Appointment
from .forms import (
    ServiceSelectionForm,
    DateSelectionForm,
    TimeSelectionForm,
    ConfirmationForm
)
from apps.services.models import Service
from apps.core.models import User
from apps.staff.models import Schedule
from apps.notifications.models import Notification
from apps.notifications.email_utils import (
    send_appointment_confirmation,
    send_staff_new_appointment,
    send_appointment_cancellation,
    send_staff_appointment_cancelled,
    send_admin_appointment_request,
    send_appointment_update
)
from .calendar_utils import get_month_calendar, get_day_schedule, get_time_slots

# Appointment Booking Views
@login_required
def booking_service(request):
    """
    Step 1: Service selection view.
    """
    # Check if the user is a client
    if request.user.role != 'client':
        messages.error(request, "Only clients can book appointments.")
        return redirect('client_portal:home')

    # Initialize the form
    form = ServiceSelectionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        # Store the selected service in the session
        request.session['booking_service_id'] = form.cleaned_data['service'].id

        # Redirect to the next step (date selection)
        return redirect('appointments:booking_date')

    return render(request, 'appointments/booking_service.html', {
        'form': form,
        'title': 'Select a Service',
        'step': 1,
        'total_steps': 2  # Now we have only 2 steps
    })

@login_required
def booking_date(request):
    """
    Step 2: Date selection view.
    """
    # Check if the user is a client
    if request.user.role != 'client':
        messages.error(request, "Only clients can book appointments.")
        return redirect('client_portal:home')

    # Check if the service was selected
    if 'booking_service_id' not in request.session:
        messages.error(request, "Please select a service first.")
        return redirect('appointments:booking_service')

    # Get the selected service
    service_id = request.session['booking_service_id']
    service = get_object_or_404(Service, id=service_id)

    # Initialize the form
    form = DateSelectionForm(request.POST or None, service_id=service_id)

    if request.method == 'POST' and form.is_valid():
        # Store the selected date in the session
        request.session['booking_date'] = form.cleaned_data['date'].isoformat()

        # Redirect directly to the confirmation step
        return redirect('appointments:booking_confirm')

    return render(request, 'appointments/booking_date.html', {
        'form': form,
        'service': service,
        'title': 'Select a Date',
        'step': 2,
        'total_steps': 2  # Now we only have 2 steps
    })

@login_required
def booking_time(request):
    """
    Step 3: Time selection view.
    """
    # Check if the user is a client
    if request.user.role != 'client':
        messages.error(request, "Only clients can book appointments.")
        return redirect('client_portal:home')

    # Check if the service and date were selected
    if 'booking_service_id' not in request.session or 'booking_date' not in request.session:
        messages.error(request, "Please complete all previous steps first.")
        return redirect('appointments:booking_service')

    # Get the selected service and date
    service_id = request.session['booking_service_id']
    date_str = request.session['booking_date']

    service = get_object_or_404(Service, id=service_id)

    try:
        date = datetime.fromisoformat(date_str).date()
    except (ValueError, TypeError):
        messages.error(request, "Invalid date format. Please select a date again.")
        return redirect('appointments:booking_date')

    # Initialize the form
    form = TimeSelectionForm(request.POST or None, service_id=service_id, date=date)

    if request.method == 'POST' and form.is_valid():
        # Store the selected time in the session
        time_str = form.cleaned_data['time']
        request.session['booking_time'] = time_str

        # Log the selected time for debugging
        print(f"Selected time: {time_str}")

        # Redirect to the confirmation step
        return redirect('appointments:booking_confirm')

    # We always have time slots available now, so this check is no longer needed

    return render(request, 'appointments/booking_time.html', {
        'form': form,
        'service': service,
        'date': date,
        'title': 'Select a Time',
        'step': 3,
        'total_steps': 3
    })

@login_required
def booking_confirm(request):
    """
    Step 3: Confirmation view.
    """
    # Check if the user is a client
    if request.user.role != 'client':
        messages.error(request, "Only clients can book appointments.")
        return redirect('client_portal:home')

    # Check if service and date are in the session
    required_keys = ['booking_service_id', 'booking_date']
    if not all(key in request.session for key in required_keys):
        messages.error(request, "Please complete all previous steps first.")
        return redirect('appointments:booking_service')

    # Get the selected service and date
    service_id = request.session['booking_service_id']
    date_str = request.session['booking_date']

    service = get_object_or_404(Service, id=service_id)

    try:
        date = datetime.fromisoformat(date_str).date()
    except (ValueError, TypeError):
        messages.error(request, "Invalid date format. Please select a date again.")
        return redirect('appointments:booking_date')

    # We don't need a specific time anymore as admin will allocate it
    # Use 9:00 AM as a placeholder for the confirmation page
    time_obj = datetime.strptime("09:00", "%H:%M").time()

    # Create a placeholder datetime for display purposes only
    # The actual appointment time will be set by the admin
    start_datetime = timezone.make_aware(datetime.combine(date, time_obj))
    end_datetime = start_datetime + timedelta(minutes=service.duration)

    # Check if the date is in the past
    if date < timezone.now().date():
        messages.error(request, "You cannot book an appointment in the past. Please select a future date.")
        return redirect('appointments:booking_date')

    # Initialize the form
    form = ConfirmationForm(request.POST or None)

    # Check if this is a direct save from the booking_date page
    direct_save = request.POST.get('direct_save') == 'true'

    # For direct save, we don't need form validation
    if request.method == 'POST' and (form.is_valid() or direct_save):
        try:
            # Find admin users to notify
            admin_users = User.objects.filter(role='admin', is_active=True)

            # Create the appointment without assigning a staff member or specific time yet
            # We'll use midnight as a placeholder time that will be updated by admin
            placeholder_time = datetime.strptime("00:00", "%H:%M").time()
            placeholder_start = timezone.make_aware(datetime.combine(date, placeholder_time))
            placeholder_end = placeholder_start + timedelta(minutes=service.duration)

            # Get notes from form if available, otherwise use empty string
            notes = ''
            if form.is_valid():
                notes = form.cleaned_data.get('notes', '')

            appointment = Appointment(
                client=request.user,
                service=service,
                start_time=placeholder_start,
                end_time=placeholder_end,
                status='pending_review',  # New status for admin review
                notes=notes
            )
            appointment.save()

            # Create notification for the client
            Notification.objects.create(
                user=request.user,
                type='appointment',
                title='Appointment Request Submitted',
                message=f"Your appointment request for {service.name} on {date.strftime('%B %d, %Y')} has been submitted. An administrator will review your request, assign a staff member, and allocate a time slot. You will be notified once your appointment is confirmed.",
                related_appointment=appointment
            )

            # Create notifications for all admin users
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    type='appointment',
                    title='New Appointment Request',
                    message=f"A new appointment request from {request.user.get_full_name()} for {service.name} on {date.strftime('%B %d, %Y')} needs review. Please assign a staff member and allocate a time slot.",
                    related_appointment=appointment
                )

            # Send email notifications
            send_appointment_confirmation(appointment)

            # Send email to admins
            for admin in admin_users:
                send_admin_appointment_request(admin, appointment)

            # Clear the booking data from the session
            session_keys = ['booking_service_id', 'booking_date', 'booking_time']
            for key in session_keys:
                if key in request.session:
                    del request.session[key]

            # Show a success message
            messages.success(request, "Your appointment has been successfully booked and saved! You can view it in your appointments page. An administrator will review your request, assign a staff member, and allocate a time slot. You will be notified once your appointment is confirmed.")

            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'success': True,
                    'message': "Your appointment has been successfully booked!",
                    'appointment_id': appointment.id,
                    'redirect_url': reverse('appointments:appointment_list')
                })
            else:
                # Redirect to the appointments list page for regular requests
                return redirect('appointments:appointment_list')
        except Exception as e:
            error_message = f"Error creating appointment: {str(e)}"
            messages.error(request, error_message)

            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=400)
            else:
                # Redirect to the booking service page for regular requests
                return redirect('appointments:booking_service')

    return render(request, 'appointments/booking_confirm.html', {
        'form': form,
        'service': service,
        'date': date,
        'time': time_obj,
        'title': 'Confirm Appointment Request',
        'step': 2,
        'total_steps': 2
    })

# Calendar Views
@login_required
def calendar_view(request, year=None, month=None):
    """
    View for displaying the calendar.
    """
    # Get the current year and month if not provided
    today = timezone.now().date()
    if not year:
        year = today.year
    if not month:
        month = today.month

    # Convert to integers
    year = int(year)
    month = int(month)

    # Get the staff member if provided
    staff_id = request.GET.get('staff')
    staff = None
    if staff_id:
        staff = get_object_or_404(User, id=staff_id, role='staff')

    # Get the calendar data
    calendar_data = get_month_calendar(year, month, staff)

    # Get all staff members
    staff_members = User.objects.filter(role='staff')

    return render(request, 'appointments/calendar.html', {
        'title': 'Calendar',
        'calendar': calendar_data,
        'staff_members': staff_members,
        'selected_staff': staff,
        'today': today,
    })

@login_required
def day_view(request, year, month, day):
    """
    View for displaying a specific day.
    """
    # Convert to integers
    year = int(year)
    month = int(month)
    day = int(day)

    # Create a date object
    date_obj = datetime(year, month, day).date()

    # Get the staff member if provided
    staff_id = request.GET.get('staff')
    staff = None
    if staff_id:
        staff = get_object_or_404(User, id=staff_id, role='staff')

    # Get the day schedule
    schedule = get_day_schedule(date_obj, staff)

    # Get all staff members
    staff_members = User.objects.filter(role='staff')

    # Get all services
    services = Service.objects.filter(is_active=True)

    # Get time slots for each service
    service_time_slots = {}
    for service in services:
        service_time_slots[service.id] = get_time_slots(date_obj, service, staff)

    return render(request, 'appointments/day_view.html', {
        'title': f'Schedule for {date_obj.strftime("%B %d, %Y")}',
        'date': date_obj,
        'schedule': schedule,
        'staff_members': staff_members,
        'selected_staff': staff,
        'services': services,
        'service_time_slots': service_time_slots,
        'range_hours': range(24),  # Add range of hours for the timeline
    })

# Appointment Management Views
@login_required
def appointment_list(request):
    """
    View for listing appointments.
    """
    # Get the user's appointments based on their role
    if request.user.role == 'client':
        appointments = Appointment.objects.filter(client=request.user)
    elif request.user.role == 'staff':
        appointments = Appointment.objects.filter(staff=request.user)
    else:  # Admin
        appointments = Appointment.objects.all()

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        appointments = appointments.filter(status=status)

    # Filter by date if provided
    date = request.GET.get('date')
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            appointments = appointments.filter(start_time__date=date_obj)
        except ValueError:
            pass

    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'title': 'My Appointments' if request.user.role == 'client' else 'Appointments'
    })

@login_required
def appointment_detail(request, appointment_id):
    """
    View for viewing appointment details.
    """
    # Get the appointment
    if request.user.role == 'client':
        appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    elif request.user.role == 'staff':
        appointment = get_object_or_404(Appointment, id=appointment_id, staff=request.user)
    else:  # Admin
        appointment = get_object_or_404(Appointment, id=appointment_id)

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'title': 'Appointment Details'
    })

@login_required
def appointment_cancel(request, appointment_id):
    """
    View for cancelling an appointment.
    """
    # Get the appointment
    if request.user.role == 'client':
        appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    elif request.user.role == 'staff':
        appointment = get_object_or_404(Appointment, id=appointment_id, staff=request.user)
    else:  # Admin
        appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if the appointment can be cancelled
    if appointment.status not in ['pending', 'confirmed']:
        messages.error(request, "This appointment cannot be cancelled.")
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)

    # Check if the appointment is in the past
    if appointment.start_time < timezone.now():
        messages.error(request, "You cannot cancel a past appointment.")
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)

    if request.method == 'POST':
        # Cancel the appointment
        appointment.status = 'cancelled'
        appointment.save()

        # Create notifications
        Notification.objects.create(
            user=appointment.client,
            type='appointment',
            title='Appointment Cancelled',
            message=f"Your appointment for {appointment.service.name} with {appointment.staff.get_full_name()} on {appointment.start_time.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')} has been cancelled.",
            related_appointment=appointment
        )

        if request.user != appointment.staff:
            Notification.objects.create(
                user=appointment.staff,
                type='appointment',
                title='Appointment Cancelled',
                message=f"The appointment for {appointment.service.name} with {appointment.client.get_full_name()} on {appointment.start_time.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')} has been cancelled.",
                related_appointment=appointment
            )

        # Send email notifications
        send_appointment_cancellation(appointment)
        send_staff_appointment_cancelled(appointment)

        # Show a success message
        messages.success(request, "The appointment has been cancelled successfully.")

        # Redirect to the appointment list
        return redirect('appointments:appointment_list')

    return render(request, 'appointments/appointment_cancel.html', {
        'appointment': appointment,
        'title': 'Cancel Appointment'
    })

@login_required
def appointment_reschedule(request, appointment_id):
    """
    View for rescheduling an appointment.
    """
    # Get the appointment
    if request.user.role == 'client':
        appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    elif request.user.role == 'staff':
        appointment = get_object_or_404(Appointment, id=appointment_id, staff=request.user)
    else:  # Admin
        appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if the appointment can be rescheduled
    if appointment.status not in ['pending', 'confirmed']:
        messages.error(request, "This appointment cannot be rescheduled.")
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)

    # Check if the appointment is in the past
    if appointment.start_time < timezone.now():
        messages.error(request, "You cannot reschedule a past appointment.")
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)

    # Store the appointment ID in the session
    request.session['reschedule_appointment_id'] = appointment.id

    # Redirect to the booking flow
    return redirect('appointments:booking_service')
