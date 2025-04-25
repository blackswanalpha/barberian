from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta

from .models import StaffSettings, Schedule
from .forms import StaffProfileForm, StaffSettingsForm, ScheduleForm
from apps.core.models import User
from apps.appointments.models import Appointment

@login_required
def staff_dashboard(request):
    """
    View for the staff dashboard.
    """
    # Check if the user is a staff member
    if request.user.role != 'staff':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get today's appointments
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        staff=request.user,
        start_time__date=today
    ).order_by('start_time')

    # Get upcoming appointments (excluding today)
    upcoming_appointments = Appointment.objects.filter(
        staff=request.user,
        start_time__date__gt=today,
        status__in=['pending', 'confirmed']
    ).order_by('start_time')[:5]

    # Get the staff member's schedule
    schedules = Schedule.objects.filter(staff=request.user).order_by('day_of_week')

    return render(request, 'staff/dashboard.html', {
        'title': 'Staff Dashboard',
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'schedules': schedules,
    })

@login_required
def staff_profile(request):
    """
    View for the staff profile.
    """
    # Check if the user is a staff member
    if request.user.role != 'staff':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = StaffProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('staff:profile')
    else:
        form = StaffProfileForm(instance=request.user)

    return render(request, 'staff/profile.html', {
        'title': 'Staff Profile',
        'form': form,
    })

@login_required
def staff_settings(request):
    """
    View for the staff settings.
    """
    # Check if the user is a staff member
    if request.user.role != 'staff':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get or create staff settings
    staff_settings, created = StaffSettings.objects.get_or_create(staff=request.user)

    if request.method == 'POST':
        form = StaffSettingsForm(request.POST, instance=staff_settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Your settings have been updated successfully.")
            return redirect('staff:settings')
    else:
        form = StaffSettingsForm(instance=staff_settings)

    return render(request, 'staff/settings.html', {
        'title': 'Staff Settings',
        'form': form,
    })

@login_required
def staff_schedule(request):
    """
    View for the staff schedule.
    """
    # Check if the user is a staff member
    if request.user.role != 'staff':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the staff member's schedule
    schedules = Schedule.objects.filter(staff=request.user).order_by('day_of_week')

    # Create schedules for missing days
    existing_days = [schedule.day_of_week for schedule in schedules]
    for day in range(7):
        if day not in existing_days:
            Schedule.objects.create(
                staff=request.user,
                day_of_week=day,
                start_time='09:00',
                end_time='17:00',
                is_working=day < 5  # Monday to Friday
            )

    # Refresh the schedules
    schedules = Schedule.objects.filter(staff=request.user).order_by('day_of_week')

    return render(request, 'staff/schedule.html', {
        'title': 'Staff Schedule',
        'schedules': schedules,
    })

@login_required
def staff_schedule_edit(request, schedule_id):
    """
    View for editing a staff schedule.
    """
    # Check if the user is a staff member
    if request.user.role != 'staff':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the schedule
    schedule = get_object_or_404(Schedule, id=schedule_id, staff=request.user)

    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Your schedule has been updated successfully.")
            return redirect('staff:schedule')
    else:
        form = ScheduleForm(instance=schedule)

    return render(request, 'staff/schedule_edit.html', {
        'title': 'Edit Schedule',
        'form': form,
        'schedule': schedule,
    })

@login_required
def staff_appointments(request):
    """
    View for the staff appointments.
    """
    # Check if the user is a staff member
    if request.user.role != 'staff':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the staff member's appointments
    appointments = Appointment.objects.filter(staff=request.user).order_by('-start_time')

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

    return render(request, 'staff/appointments.html', {
        'title': 'Staff Appointments',
        'appointments': appointments,
    })

@login_required
def staff_appointment_detail(request, appointment_id):
    """
    View for the staff appointment detail.
    """
    # Check if the user is a staff member
    if request.user.role != 'staff':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id, staff=request.user)

    return render(request, 'staff/appointment_detail.html', {
        'title': 'Appointment Detail',
        'appointment': appointment,
    })

@login_required
def staff_appointment_update(request, appointment_id):
    """
    View for updating an appointment status.
    """
    # Check if the user is a staff member
    if request.user.role != 'staff':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id, staff=request.user)

    # Get the new status
    new_status = request.POST.get('status')
    if new_status in ['confirmed', 'completed', 'no_show', 'cancelled']:
        # Update the appointment status
        appointment.status = new_status
        appointment.save()

        # Show a success message
        messages.success(request, f"The appointment has been marked as {new_status}.")
    else:
        # Show an error message
        messages.error(request, "Invalid status.")

    # Redirect to the appointment detail page
    return redirect('staff:appointment_detail', appointment_id=appointment.id)
