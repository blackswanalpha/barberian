from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from datetime import datetime, timedelta, time
import json
import calendar as cal
import base64
from io import BytesIO
from PIL import Image, ImageEnhance, ImageOps

from .models import Report, ReportExport, UserLog
from .forms import (
    UserForm, UserEditForm, BusinessSettingsForm, BusinessHoursForm,
    HolidayForm, CategoryForm, ServiceForm, ReportForm, StaffForm, StaffEditForm
)
from apps.core.models import User, BusinessSettings, BusinessHours, Holiday
from apps.services.models import Category, Service, ServiceMedia
from apps.appointments.models import Appointment
from apps.payments.models import Payment, Invoice
from apps.reviews.models import Review
from apps.staff.models import Schedule, StaffSettings
from apps.notifications.models import Notification

@login_required
def admin_approve_appointment(request, appointment_id):
    """
    View for approving a single appointment.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Approve the appointment
    approved_count = approve_appointments(request, [appointment_id])

    if approved_count > 0:
        messages.success(request, "Appointment has been approved and staff assigned.")
    else:
        messages.error(request, "Failed to approve appointment. It may have already been processed.")

    # Redirect back to the pending appointments page
    return redirect('admin_panel:pending_appointments')

def approve_appointments(request, appointment_ids):
    """
    Helper function to approve multiple appointments.
    Returns the number of successfully approved appointments.
    """
    approved_count = 0

    # Get all staff members
    staff_members = User.objects.filter(role='staff', is_active=True)

    for appointment_id in appointment_ids:
        try:
            with transaction.atomic():
                # Get the appointment
                appointment = Appointment.objects.get(id=appointment_id, status='pending_review')

                # Get the day of the week for the appointment
                day_of_week = appointment.start_time.weekday()

                # Find an available staff member
                assigned_staff = None

                for staff in staff_members:
                    try:
                        # Check if the staff member is working on this day
                        schedule = Schedule.objects.get(staff=staff, day_of_week=day_of_week, is_working=True)

                        # Check if the appointment is within the staff's working hours
                        staff_start = timezone.make_aware(datetime.combine(appointment.start_time.date(), schedule.start_time))
                        staff_end = timezone.make_aware(datetime.combine(appointment.start_time.date(), schedule.end_time))

                        if appointment.start_time >= staff_start and appointment.end_time <= staff_end:
                            # Check if the staff member has any overlapping appointments
                            overlapping_appointments = Appointment.objects.filter(
                                staff=staff,
                                start_time__lt=appointment.end_time,
                                end_time__gt=appointment.start_time,
                                status__in=['pending', 'confirmed']
                            )

                            if not overlapping_appointments.exists():
                                assigned_staff = staff
                                break
                    except Schedule.DoesNotExist:
                        # Staff member is not working on this day
                        continue

                # If no staff is available, assign to the first staff member
                if not assigned_staff and staff_members.exists():
                    assigned_staff = staff_members.first()

                # Update the appointment
                if assigned_staff:
                    appointment.staff = assigned_staff
                    appointment.status = 'confirmed'
                    appointment.save()

                    # Create notifications
                    Notification.objects.create(
                        user=appointment.client,
                        type='appointment',
                        title='Appointment Confirmed',
                        message=f"Your appointment for {appointment.service.name} has been confirmed for {appointment.start_time.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')} with {appointment.staff.get_full_name()}.",
                        related_appointment=appointment
                    )

                    Notification.objects.create(
                        user=appointment.staff,
                        type='appointment',
                        title='New Appointment Assigned',
                        message=f"You have been assigned a new appointment for {appointment.service.name} with {appointment.client.get_full_name()} on {appointment.start_time.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')}.",
                        related_appointment=appointment
                    )

                    # Send email notifications
                    from apps.notifications.email_utils import send_appointment_update, send_staff_new_appointment
                    changes = {'status': 'Confirmed', 'staff': assigned_staff.get_full_name()}
                    send_appointment_update(appointment, changes)
                    send_staff_new_appointment(appointment)

                    approved_count += 1
        except Appointment.DoesNotExist:
            # Appointment not found or not in pending_review status
            continue
        except Exception as e:
            # Log the error
            print(f"Error approving appointment {appointment_id}: {str(e)}")
            continue

    return approved_count

@login_required
def admin_dashboard(request):
    """
    View for the admin dashboard.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get statistics for the dashboard
    today = timezone.now().date()

    # Appointments statistics
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(start_time__date=today).order_by('start_time')
    pending_appointments = Appointment.objects.filter(status='pending').count()
    pending_review_appointments = Appointment.objects.filter(status='pending_review').count()

    # User statistics
    total_clients = User.objects.filter(role='client').count()
    total_staff = User.objects.filter(role='staff').count()

    # Service statistics
    total_services = Service.objects.count()

    # Payment statistics
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0

    # Review statistics
    pending_review_count = Review.objects.filter(is_approved=False).count()
    recent_reviews = Review.objects.order_by('-created_at')[:5]

    # Recent appointments
    recent_appointments = Appointment.objects.order_by('-created_at')[:5]

    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:5]

    return render(request, 'admin_panel/dashboard.html', {
        'title': 'Admin Dashboard',
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'pending_review_appointments': pending_review_appointments,
        'total_clients': total_clients,
        'total_staff': total_staff,
        'total_services': total_services,
        'total_revenue': total_revenue,
        'pending_review_count': pending_review_count,
        'recent_reviews': recent_reviews,
        'recent_appointments': recent_appointments,
        'recent_users': recent_users,
        'client_count': total_clients,
        'appointment_count': total_appointments,
        'pending_count': pending_review_appointments,  # Add this for the sidebar badge
    })

@login_required
def admin_users(request):
    """
    View for managing users.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all users
    users = User.objects.all().order_by('-date_joined')

    # Filter by role if provided
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)

    # Filter by search query if provided
    query = request.GET.get('q')
    if query:
        users = users.filter(
            first_name__icontains=query
        ) | users.filter(
            last_name__icontains=query
        ) | users.filter(
            email__icontains=query
        )

    return render(request, 'admin_panel/users.html', {
        'title': 'Users',
        'users': users,
    })

@login_required
def admin_user_create(request):
    """
    View for creating a new user.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect('admin_panel:users')
    else:
        form = UserForm()

    return render(request, 'admin_panel/user_form.html', {
        'title': 'Create User',
        'form': form,
    })

@login_required
def admin_user_edit(request, user_id):
    """
    View for editing a user.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the user
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect('admin_panel:users')
    else:
        form = UserEditForm(instance=user)

    return render(request, 'admin_panel/user_form.html', {
        'title': 'Edit User',
        'form': form,
        'user_obj': user,
    })

@login_required
def admin_user_delete(request, user_id):
    """
    View for deleting a user.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the user
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('admin_panel:users')

    return render(request, 'admin_panel/user_delete.html', {
        'title': 'Delete User',
        'user_obj': user,
    })

@login_required
def admin_business_settings(request):
    """
    View for managing business settings.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get or create business settings
    business_settings, created = BusinessSettings.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = BusinessSettingsForm(request.POST, request.FILES, instance=business_settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Business settings updated successfully.")
            return redirect('admin_panel:business_settings')
    else:
        form = BusinessSettingsForm(instance=business_settings)

    return render(request, 'admin_panel/business_settings.html', {
        'title': 'Business Settings',
        'form': form,
    })

@login_required
def admin_business_hours(request):
    """
    View for managing business hours.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all business hours
    business_hours = BusinessHours.objects.all().order_by('day_of_week')

    # Create business hours for missing days
    existing_days = [hour.day_of_week for hour in business_hours]
    for day in range(7):
        if day not in existing_days:
            BusinessHours.objects.create(
                day_of_week=day,
                is_open=day < 5,  # Monday to Friday
                opening_time='09:00',
                closing_time='17:00'
            )

    # Refresh the business hours
    business_hours = BusinessHours.objects.all().order_by('day_of_week')

    return render(request, 'admin_panel/business_hours.html', {
        'title': 'Business Hours',
        'business_hours': business_hours,
    })

@login_required
def admin_business_hour_edit(request, hour_id):
    """
    View for editing a business hour.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the business hour
    business_hour = get_object_or_404(BusinessHours, id=hour_id)

    if request.method == 'POST':
        form = BusinessHoursForm(request.POST, instance=business_hour)
        if form.is_valid():
            form.save()
            messages.success(request, "Business hour updated successfully.")
            return redirect('admin_panel:business_hours')
    else:
        form = BusinessHoursForm(instance=business_hour)

    return render(request, 'admin_panel/business_hour_form.html', {
        'title': 'Edit Business Hour',
        'form': form,
        'business_hour': business_hour,
    })

@login_required
def admin_holidays(request):
    """
    View for managing holidays.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all holidays
    holidays = Holiday.objects.all().order_by('date')

    return render(request, 'admin_panel/holidays.html', {
        'title': 'Holidays',
        'holidays': holidays,
    })

@login_required
def admin_holiday_create(request):
    """
    View for creating a new holiday.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Holiday created successfully.")
            return redirect('admin_panel:holidays')
    else:
        form = HolidayForm()

    return render(request, 'admin_panel/holiday_form.html', {
        'title': 'Create Holiday',
        'form': form,
    })

@login_required
def admin_holiday_edit(request, holiday_id):
    """
    View for editing a holiday.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the holiday
    holiday = get_object_or_404(Holiday, id=holiday_id)

    if request.method == 'POST':
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, "Holiday updated successfully.")
            return redirect('admin_panel:holidays')
    else:
        form = HolidayForm(instance=holiday)

    return render(request, 'admin_panel/holiday_form.html', {
        'title': 'Edit Holiday',
        'form': form,
        'holiday': holiday,
    })

@login_required
def admin_holiday_delete(request, holiday_id):
    """
    View for deleting a holiday.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the holiday
    holiday = get_object_or_404(Holiday, id=holiday_id)

    if request.method == 'POST':
        holiday.delete()
        messages.success(request, "Holiday deleted successfully.")
        return redirect('admin_panel:holidays')

    return render(request, 'admin_panel/holiday_delete.html', {
        'title': 'Delete Holiday',
        'holiday': holiday,
    })

@login_required
def admin_categories(request):
    """
    View for managing service categories.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all categories
    categories = Category.objects.all().order_by('name')

    return render(request, 'admin_panel/categories.html', {
        'title': 'Service Categories',
        'categories': categories,
    })

@login_required
def admin_category_create(request):
    """
    View for creating a new service category.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm()

    return render(request, 'admin_panel/category_form.html', {
        'title': 'Create Category',
        'form': form,
    })

@login_required
def admin_category_edit(request, category_id):
    """
    View for editing a service category.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the category
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin_panel/category_form.html', {
        'title': 'Edit Category',
        'form': form,
        'category': category,
    })

@login_required
def admin_category_delete(request, category_id):
    """
    View for deleting a service category.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the category
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('admin_panel:categories')

    return render(request, 'admin_panel/category_delete.html', {
        'title': 'Delete Category',
        'category': category,
    })

@login_required
def admin_services(request):
    """
    View for managing services.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all services
    services = Service.objects.all().order_by('category', 'name')

    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        services = services.filter(category_id=category_id)

    # Filter by search query if provided
    query = request.GET.get('q')
    if query:
        services = services.filter(name__icontains=query) | services.filter(description__icontains=query)

    return render(request, 'admin_panel/services.html', {
        'title': 'Services',
        'services': services,
        'categories': Category.objects.all(),
    })

@login_required
def admin_service_create(request):
    """
    View for creating a new service.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service created successfully.")
            return redirect('admin_panel:services')
    else:
        form = ServiceForm()

    return render(request, 'admin_panel/service_form.html', {
        'title': 'Create Service',
        'form': form,
    })

@login_required
def admin_service_edit(request, service_id):
    """
    View for editing a service.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the service
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully.")
            return redirect('admin_panel:services')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'admin_panel/service_form.html', {
        'title': 'Edit Service',
        'form': form,
        'service': service,
    })

@login_required
def admin_service_delete(request, service_id):
    """
    View for deleting a service.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the service
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        service.delete()
        messages.success(request, "Service deleted successfully.")
        return redirect('admin_panel:services')

    return render(request, 'admin_panel/service_delete.html', {
        'title': 'Delete Service',
        'service': service,
    })

@login_required
def admin_appointments(request):
    """
    View for managing appointments.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all appointments
    appointments = Appointment.objects.all().order_by('-start_time')

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

    # Filter by staff if provided
    staff_id = request.GET.get('staff')
    if staff_id:
        appointments = appointments.filter(staff_id=staff_id)

    # Filter by client if provided
    client_id = request.GET.get('client')
    if client_id:
        appointments = appointments.filter(client_id=client_id)

    return render(request, 'admin_panel/appointments.html', {
        'title': 'Appointments',
        'appointments': appointments,
        'staff_members': User.objects.filter(role='staff'),
        'clients': User.objects.filter(role='client'),
    })

@login_required
def admin_appointment_detail(request, appointment_id):
    """
    View for viewing appointment details.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id)

    return render(request, 'admin_panel/appointment_detail.html', {
        'title': 'Appointment Detail',
        'appointment': appointment,
    })

@login_required
def admin_appointment_update(request, appointment_id):
    """
    View for updating an appointment status.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        # Get form data
        service_id = request.POST.get('service_id')
        staff_id = request.POST.get('staff_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        notes = request.POST.get('notes', '')
        status = request.POST.get('status')
        notify_client = request.POST.get('notify_client') == 'on'

        # Track changes for notification
        changes = {}

        try:
            # Update service if changed
            if service_id:
                service_id_int = int(service_id)
                if service_id_int != appointment.service.id:
                    old_service = appointment.service.name
                    service = Service.objects.get(id=service_id)
                    appointment.service = service
                    changes['service'] = f"from {old_service} to {service.name}"

            # Update staff if changed
            if staff_id:
                staff_id_int = int(staff_id)
                current_staff_id = appointment.staff.id if appointment.staff else None
                if staff_id_int != current_staff_id:
                    old_staff = appointment.staff.get_full_name() if appointment.staff else "Not assigned"
                    staff = User.objects.get(id=staff_id, role='staff')
                    appointment.staff = staff
                    changes['staff'] = f"from {old_staff} to {staff.get_full_name()}"

            # Update date and time if changed
            if date_str and time_str:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                time_obj = datetime.strptime(time_str, '%H:%M').time()
                new_start = timezone.make_aware(datetime.combine(date_obj, time_obj))

                if new_start != appointment.start_time:
                    old_datetime = appointment.start_time.strftime('%B %d, %Y at %I:%M %p')
                    appointment.start_time = new_start
                    appointment.end_time = new_start + timedelta(minutes=appointment.service.duration)
                    changes['datetime'] = f"from {old_datetime} to {new_start.strftime('%B %d, %Y at %I:%M %p')}"

            # Update notes if changed
            if notes != appointment.notes:
                appointment.notes = notes
                changes['notes'] = "updated"

            # Update status if changed
            if status and status != appointment.status:
                old_status = appointment.status.title()
                appointment.status = status
                changes['status'] = f"from {old_status} to {status.title()}"

            # Save the appointment
            appointment.save()

            # Log the update
            UserLog.objects.create(
                user=request.user,
                action='update',
                entity_type='appointment',
                entity_id=appointment.id,
                details=f"Updated appointment: {', '.join([f'{k} {v}' for k, v in changes.items()])}"
            )

            # Notify client if requested
            if notify_client and changes:
                # Create notification
                Notification.objects.create(
                    user=appointment.client,
                    type='appointment',
                    title='Appointment Updated',
                    message=f"Your appointment for {appointment.service.name} has been updated. New details: {appointment.start_time.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')} with {appointment.staff.get_full_name() if appointment.staff else 'TBD'}.",
                    related_appointment=appointment
                )

                # Send email notification
                # This would be implemented with an email notification system

            # Show success message
            messages.success(request, "Appointment updated successfully.")

            # Redirect to appointment detail
            return redirect('admin_panel:appointment_detail', appointment_id=appointment.id)

        except User.DoesNotExist:
            messages.error(request, "Staff member not found.")
        except Service.DoesNotExist:
            messages.error(request, "Service not found.")
        except Exception as e:
            messages.error(request, f"Error updating appointment: {str(e)}")

        # If there was an error, redirect back to the edit page
        return redirect('admin_panel:appointment_edit', appointment_id=appointment.id)

    # Simple status update (from detail page)
    new_status = request.POST.get('status')
    if new_status in ['pending', 'confirmed', 'cancelled', 'completed', 'no_show']:
        # Update the appointment status
        old_status = appointment.status.title()
        appointment.status = new_status
        appointment.save()

        # Log the change
        UserLog.objects.create(
            user=request.user,
            action='update',
            entity_type='appointment',
            entity_id=appointment.id,
            details=f"Updated status from {old_status} to {new_status.title()}"
        )

        # Show a success message
        messages.success(request, f"The appointment has been marked as {new_status}.")

    # Redirect to the appointment detail page
    return redirect('admin_panel:appointment_detail', appointment_id=appointment.id)

@login_required
def admin_appointment_edit(request, appointment_id):
    """
    View for editing an appointment.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Get all services and staff members
    services = Service.objects.filter(is_active=True)
    staff_members = User.objects.filter(role='staff', is_active=True)

    return render(request, 'admin_panel/appointment_edit_modern.html', {
        'title': 'Edit Appointment',
        'appointment': appointment,
        'services': services,
        'staff_members': staff_members,
    })

@login_required
def admin_appointment_delete(request, appointment_id):
    """
    View for deleting an appointment.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        # Log the deletion
        UserLog.objects.create(
            user=request.user,
            action='delete',
            entity_type='appointment',
            entity_id=appointment.id,
            details=f"Deleted appointment for {appointment.client.get_full_name() if appointment.client else 'Unknown Client'} on {appointment.start_time.strftime('%Y-%m-%d %H:%M')}"
        )

        # Delete the appointment
        appointment.delete()

        # Show a success message
        messages.success(request, "Appointment deleted successfully.")

        # Redirect to the appointments list
        return redirect('admin_panel:appointments')

    # If not POST, render the confirmation page
    return render(request, 'admin_panel/appointment_delete.html', {
        'title': 'Delete Appointment',
        'appointment': appointment,
    })

@login_required
def admin_pending_appointments(request):
    """
    View for managing pending appointments.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all pending appointments
    appointments = Appointment.objects.filter(status='pending').order_by('-start_time')

    # Filter by date if provided
    date = request.GET.get('date')
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            appointments = appointments.filter(start_time__date=date_obj)
        except ValueError:
            pass

    # Filter by service if provided
    service_id = request.GET.get('service')
    if service_id:
        appointments = appointments.filter(service_id=service_id)

    # Filter by client if provided
    client_id = request.GET.get('client')
    if client_id:
        appointments = appointments.filter(client_id=client_id)

    return render(request, 'admin_panel/pending_appointments.html', {
        'title': 'Pending Appointments',
        'appointments': appointments,
        'staff_members': User.objects.filter(role='staff'),
        'services': Service.objects.all(),
        'clients': User.objects.filter(role='client'),
    })

@login_required
def admin_review_appointment(request, appointment_id):
    """
    View for reviewing a pending appointment.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        # Update the appointment
        status = request.POST.get('status')
        staff_id = request.POST.get('staff_id')
        notes = request.POST.get('notes', '')

        if status and staff_id:
            # Update appointment
            appointment.status = status
            appointment.staff_id = staff_id
            appointment.notes = notes
            appointment.save()

            # Log the change
            UserLog.objects.create(
                user=request.user,
                action='update',
                entity_type='appointment',
                entity_id=appointment.id,
                details=f"Reviewed appointment: {status}"
            )

            # Send notification to client
            # This would be implemented with a notification system
            messages.success(request, "Appointment updated successfully.")
            return redirect('admin_panel:pending_appointments_modern')
        else:
            messages.error(request, "Please provide all required information.")

    # Get all staff members
    staff_members = User.objects.filter(role='staff')

    return render(request, 'admin_panel/appointment_review.html', {
        'title': 'Review Appointment',
        'appointment': appointment,
        'staff_members': staff_members,
    })

@login_required
def admin_bulk_assign_staff(request):
    """
    View for bulk assigning staff to pending appointments.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        service_id = request.POST.get('service_id')
        date_filter = request.POST.get('date_filter')

        if not staff_id:
            messages.error(request, "Please select a staff member.")
            return redirect('admin_panel:pending_appointments_modern')

        # Build the query
        query = {'status': 'pending'}

        if service_id:
            query['service_id'] = service_id

        if date_filter:
            today = timezone.now().date()

            if date_filter == 'today':
                query['start_time__date'] = today
            elif date_filter == 'tomorrow':
                query['start_time__date'] = today + timedelta(days=1)
            elif date_filter == 'this-week':
                # Get the start and end of the current week
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                query['start_time__date__gte'] = start_of_week
                query['start_time__date__lte'] = end_of_week

        # Update appointments
        appointments = Appointment.objects.filter(**query)
        count = appointments.count()

        if count > 0:
            appointments.update(staff_id=staff_id, status='confirmed')

            # Log the bulk update
            UserLog.objects.create(
                user=request.user,
                action='update',
                entity_type='bulk_appointments',
                entity_id=0,
                details=f"Bulk assigned {count} appointments to staff ID {staff_id}"
            )

            messages.success(request, f"{count} appointments have been assigned to staff and confirmed.")
        else:
            messages.info(request, "No appointments matched your criteria.")

        return redirect('admin_panel:pending_appointments_modern')

    return redirect('admin_panel:pending_appointments_modern')

@login_required
def admin_reports(request):
    """
    View for managing reports.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all reports
    reports = Report.objects.all().order_by('-created_at')

    return render(request, 'admin_panel/reports.html', {
        'title': 'Reports',
        'reports': reports,
    })

@login_required
def admin_report_create(request):
    """
    View for creating a new report.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            messages.success(request, "Report created successfully.")
            return redirect('admin_panel:reports')
    else:
        form = ReportForm()

    return render(request, 'admin_panel/report_form.html', {
        'title': 'Create Report',
        'form': form,
    })

@login_required
def admin_report_detail(request, report_id):
    """
    View for viewing report details.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the report
    report = get_object_or_404(Report, id=report_id)

    # Generate report data based on the report type
    data = {}

    if report.type == 'appointments':
        # Get appointment statistics
        total_appointments = Appointment.objects.count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
        cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        no_show_appointments = Appointment.objects.filter(status='no_show').count()

        data = {
            'total_appointments': total_appointments,
            'pending_appointments': pending_appointments,
            'confirmed_appointments': confirmed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'completed_appointments': completed_appointments,
            'no_show_appointments': no_show_appointments,
        }

    elif report.type == 'revenue':
        # Get revenue statistics
        total_revenue = Appointment.objects.filter(status='completed').aggregate(
            total=Sum('service__price')
        )['total'] or 0

        # Get revenue by service
        revenue_by_service = []
        service_data = Appointment.objects.filter(status='completed').values(
            'service__name'
        ).annotate(
            total=Sum('service__price')
        ).order_by('-total')

        for item in service_data:
            revenue_by_service.append({
                'service__name': item['service__name'],
                'total': float(item['total']) if item['total'] else 0
            })

        # Get revenue by staff
        revenue_by_staff = []
        staff_data = Appointment.objects.filter(status='completed').values(
            'staff__first_name', 'staff__last_name'
        ).annotate(
            total=Sum('service__price')
        ).order_by('-total')

        for item in staff_data:
            revenue_by_staff.append({
                'staff__first_name': item['staff__first_name'],
                'staff__last_name': item['staff__last_name'],
                'total': float(item['total']) if item['total'] else 0
            })

        data = {
            'total_revenue': float(total_revenue),
            'revenue_by_service': revenue_by_service,
            'revenue_by_staff': revenue_by_staff,
        }

    elif report.type == 'staff_performance':
        # Get staff performance statistics
        staff_performance_data = Appointment.objects.values(
            'staff__first_name', 'staff__last_name'
        ).annotate(
            total_appointments=Count('id'),
            completed_appointments=Count('id', filter=Q(status='completed')),
            cancelled_appointments=Count('id', filter=Q(status='cancelled')),
            no_show_appointments=Count('id', filter=Q(status='no_show')),
        ).order_by('-total_appointments')

        # Convert QuerySet to list to avoid serialization issues
        staff_performance_list = []
        for item in staff_performance_data:
            staff_performance_list.append({
                'staff__first_name': item['staff__first_name'],
                'staff__last_name': item['staff__last_name'],
                'total_appointments': item['total_appointments'],
                'completed_appointments': item['completed_appointments'],
                'cancelled_appointments': item['cancelled_appointments'],
                'no_show_appointments': item['no_show_appointments']
            })

        data = {
            'staff_performance': staff_performance_list,
        }

    elif report.type == 'client_activity':
        # Get client activity statistics
        client_activity_data = Appointment.objects.values(
            'client__first_name', 'client__last_name'
        ).annotate(
            total_appointments=Count('id'),
            completed_appointments=Count('id', filter=Q(status='completed')),
            cancelled_appointments=Count('id', filter=Q(status='cancelled')),
            no_show_appointments=Count('id', filter=Q(status='no_show')),
        ).order_by('-total_appointments')

        # Convert QuerySet to list to avoid serialization issues
        client_activity_list = []
        for item in client_activity_data:
            client_activity_list.append({
                'client__first_name': item['client__first_name'],
                'client__last_name': item['client__last_name'],
                'total_appointments': item['total_appointments'],
                'completed_appointments': item['completed_appointments'],
                'cancelled_appointments': item['cancelled_appointments'],
                'no_show_appointments': item['no_show_appointments']
            })

        data = {
            'client_activity': client_activity_list,
        }

    elif report.type == 'services':
        # Get service statistics
        service_statistics_data = Appointment.objects.values(
            'service__name'
        ).annotate(
            total_appointments=Count('id'),
            completed_appointments=Count('id', filter=Q(status='completed')),
            cancelled_appointments=Count('id', filter=Q(status='cancelled')),
            no_show_appointments=Count('id', filter=Q(status='no_show')),
        ).order_by('-total_appointments')

        # Convert QuerySet to list to avoid serialization issues
        service_statistics_list = []
        for item in service_statistics_data:
            service_statistics_list.append({
                'service__name': item['service__name'],
                'total_appointments': item['total_appointments'],
                'completed_appointments': item['completed_appointments'],
                'cancelled_appointments': item['cancelled_appointments'],
                'no_show_appointments': item['no_show_appointments']
            })

        data = {
            'service_statistics': service_statistics_list,
        }

    return render(request, 'admin_panel/report_detail.html', {
        'title': 'Report Detail',
        'report': report,
        'data': data,
    })

@login_required
def admin_report_delete(request, report_id):
    """
    View for deleting a report.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the report
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        report.delete()
        messages.success(request, "Report deleted successfully.")
        return redirect('admin_panel:reports')

    return render(request, 'admin_panel/report_delete.html', {
        'title': 'Delete Report',
        'report': report,
    })

@login_required
def admin_reviews(request):
    """
    View for managing reviews.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all reviews
    reviews = Review.objects.all().order_by('-created_at')

    # Filter by approval status if provided
    approval_status = request.GET.get('approval_status')
    if approval_status == 'approved':
        reviews = reviews.filter(is_approved=True)
    elif approval_status == 'pending':
        reviews = reviews.filter(is_approved=False)

    # Filter by rating if provided
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=rating)

    # Filter by staff if provided
    staff_id = request.GET.get('staff')
    if staff_id:
        reviews = reviews.filter(staff_id=staff_id)

    # Filter by service if provided
    service_id = request.GET.get('service')
    if service_id:
        reviews = reviews.filter(service_id=service_id)

    return render(request, 'reviews/admin_review_list.html', {
        'title': 'Manage Reviews',
        'reviews': reviews,
        'approval_status': approval_status,
        'staff_members': User.objects.filter(role='staff'),
        'services': Service.objects.all(),
    })

@login_required
def admin_logs(request):
    """
    View for viewing user activity logs.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all logs
    logs = UserLog.objects.all().order_by('-created_at')

    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)

    # Filter by action if provided
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)

    # Filter by entity type if provided
    entity_type = request.GET.get('entity_type')
    if entity_type:
        logs = logs.filter(entity_type=entity_type)

    return render(request, 'admin_panel/logs.html', {
        'title': 'User Activity Logs',
        'logs': logs,
        'users': User.objects.all(),
    })

@login_required
def admin_staff(request):
    """
    View for managing staff members.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all staff members
    staff_members = User.objects.filter(role='staff').order_by('-date_joined')

    # Filter by status if provided
    status = request.GET.get('status')
    if status == 'active':
        staff_members = staff_members.filter(is_active=True)
    elif status == 'inactive':
        staff_members = staff_members.filter(is_active=False)

    # Filter by search query if provided
    query = request.GET.get('q')
    if query:
        staff_members = staff_members.filter(
            first_name__icontains=query
        ) | staff_members.filter(
            last_name__icontains=query
        ) | staff_members.filter(
            email__icontains=query
        ) | staff_members.filter(
            username__icontains=query
        )

    return render(request, 'admin_panel/staff.html', {
        'title': 'Staff Management',
        'staff_members': staff_members,
    })

@login_required
def admin_staff_create(request):
    """
    View for creating a new staff member.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member created successfully.")
            return redirect('admin_panel:staff')
    else:
        form = StaffForm()

    return render(request, 'admin_panel/staff_form.html', {
        'title': 'Create Staff Member',
        'form': form,
    })

@login_required
def admin_staff_edit(request, staff_id):
    """
    View for editing a staff member.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the staff member
    staff = get_object_or_404(User, id=staff_id, role='staff')

    if request.method == 'POST':
        form = StaffEditForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member updated successfully.")
            return redirect('admin_panel:staff')
    else:
        form = StaffEditForm(instance=staff)

    return render(request, 'admin_panel/staff_form.html', {
        'title': 'Edit Staff Member',
        'form': form,
        'staff': staff,
    })

@login_required
def admin_staff_delete(request, staff_id):
    """
    View for deleting a staff member.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the staff member
    staff = get_object_or_404(User, id=staff_id, role='staff')

    if request.method == 'POST':
        staff.delete()
        messages.success(request, "Staff member deleted successfully.")
        return redirect('admin_panel:staff')

    return render(request, 'admin_panel/staff_delete.html', {
        'title': 'Delete Staff Member',
        'staff': staff,
    })

@login_required
def admin_staff_schedule(request):
    """
    View for managing staff schedules.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all staff members
    staff_members = User.objects.filter(role='staff')

    # Get selected staff member
    staff_id = request.GET.get('staff')
    selected_staff = None

    if staff_id:
        try:
            selected_staff = User.objects.get(id=staff_id, role='staff')
        except User.DoesNotExist:
            messages.error(request, "Staff member not found.")
            return redirect('admin_panel:staff_schedule')

    # If no staff member is selected, redirect to the first one
    if not selected_staff and staff_members.exists():
        return redirect(f"{request.path}?staff={staff_members.first().id}")

    # Get schedules for the selected staff member
    days_of_week = []

    if selected_staff:
        # Get or create staff settings
        staff_settings, created = StaffSettings.objects.get_or_create(staff=selected_staff)

        # Get schedules for each day of the week
        for day_value, day_name in Schedule.DAYS_OF_WEEK:
            # Get or create schedule for this day
            schedule, created = Schedule.objects.get_or_create(
                staff=selected_staff,
                day_of_week=day_value,
                defaults={
                    'is_working': True,
                    'start_time': time(9, 0),
                    'end_time': time(17, 0)
                }
            )

            days_of_week.append({
                'value': day_value,
                'name': day_name,
                'schedule': schedule
            })

        # Get upcoming appointments for this staff member
        upcoming_appointments = Appointment.objects.filter(
            staff=selected_staff,
            start_time__gte=timezone.now()
        ).order_by('start_time')[:10]
    else:
        upcoming_appointments = []

    return render(request, 'admin_panel/staff_schedule.html', {
        'title': 'Staff Schedule',
        'staff_members': staff_members,
        'selected_staff': selected_staff,
        'days_of_week': days_of_week,
        'upcoming_appointments': upcoming_appointments,
    })

@login_required
def admin_staff_schedule_save(request, staff_id):
    """
    View for saving staff schedules.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the staff member
    staff = get_object_or_404(User, id=staff_id, role='staff')

    if request.method == 'POST':
        # Process each day of the week
        for day_value, day_name in Schedule.DAYS_OF_WEEK:
            # Check if the day is available
            is_working = request.POST.get(f'available_{day_value}') == 'on'

            # Get times
            start_time_str = request.POST.get(f'start_time_{day_value}')
            end_time_str = request.POST.get(f'end_time_{day_value}')

            # Parse times
            try:
                start_time = datetime.strptime(start_time_str, '%H:%M').time() if start_time_str else time(9, 0)
                end_time = datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else time(17, 0)
            except ValueError:
                messages.error(request, f"Invalid time format for {day_name}.")
                return redirect('admin_panel:staff_schedule', staff_id=staff_id)

            # Update or create schedule
            schedule, created = Schedule.objects.update_or_create(
                staff=staff,
                day_of_week=day_value,
                defaults={
                    'is_working': is_working,
                    'start_time': start_time,
                    'end_time': end_time
                }
            )

        messages.success(request, "Schedule updated successfully.")

    return redirect(f"{reverse('admin_panel:staff_schedule')}?staff={staff_id}")

@login_required
def admin_staff_timeoff_add(request, staff_id):
    """
    View for adding time off for a staff member.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the staff member
    staff = get_object_or_404(User, id=staff_id, role='staff')

    if request.method == 'POST':
        # Get form data
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        reason = request.POST.get('reason', '')
        status = request.POST.get('status', 'pending')

        # Validate dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if end_date < start_date:
                messages.error(request, "End date cannot be before start date.")
                return redirect('admin_panel:staff_schedule', staff_id=staff_id)

        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('admin_panel:staff_schedule', staff_id=staff_id)

        # For now, just log the request since we don't have a TimeOff model
        UserLog.objects.create(
            user=request.user,
            action='create',
            entity_type='staff_timeoff',
            entity_id=staff.id,
            details=f"Added time off for {staff.get_full_name()} from {start_date} to {end_date}: {reason} ({status})"
        )

        messages.success(request, "Time off added successfully.")

    return redirect(f"{reverse('admin_panel:staff_schedule')}?staff={staff_id}")

@login_required
def admin_staff_timeoff_edit(request, timeoff_id):
    """
    View for editing time off for a staff member.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # For now, just log the request since we don't have a TimeOff model
    if request.method == 'POST':
        # Get form data
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        reason = request.POST.get('reason', '')
        status = request.POST.get('status', 'pending')

        # Validate dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if end_date < start_date:
                messages.error(request, "End date cannot be before start date.")
                return redirect('admin_panel:staff_schedule')

        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('admin_panel:staff_schedule')

        # Log the edit
        UserLog.objects.create(
            user=request.user,
            action='update',
            entity_type='staff_timeoff',
            entity_id=timeoff_id,
            details=f"Updated time off (ID: {timeoff_id}) from {start_date} to {end_date}: {reason} ({status})"
        )

        messages.success(request, "Time off updated successfully.")

    return redirect('admin_panel:staff_schedule')

@login_required
def admin_staff_timeoff_delete(request, timeoff_id):
    """
    View for deleting time off for a staff member.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # For now, just log the request since we don't have a TimeOff model
    UserLog.objects.create(
        user=request.user,
        action='delete',
        entity_type='staff_timeoff',
        entity_id=timeoff_id,
        details=f"Deleted time off (ID: {timeoff_id})"
    )

    messages.success(request, "Time off deleted successfully.")

    return redirect('admin_panel:staff_schedule')

@login_required
def admin_staff_performance(request):
    """
    View for staff performance metrics.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all staff members
    staff_members = User.objects.filter(role='staff')

    # Get selected staff member
    staff_id = request.GET.get('staff')
    selected_staff = None

    if staff_id:
        try:
            selected_staff = User.objects.get(id=staff_id, role='staff')
        except User.DoesNotExist:
            messages.error(request, "Staff member not found.")
            return redirect('admin_panel:staff_performance')

    # If no staff member is selected, redirect to the first one
    if not selected_staff and staff_members.exists():
        return redirect(f"{request.path}?staff={staff_members.first().id}")

    # Get date range
    date_range = request.GET.get('range', '30')

    if date_range == 'custom':
        # Custom date range
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            # Default to last 30 days if invalid dates
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    else:
        # Preset date range
        try:
            days = int(date_range)
        except ValueError:
            days = 30

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

    # Get metrics for the selected staff member
    metrics = {}

    if selected_staff:
        # Get appointments in the date range
        appointments = Appointment.objects.filter(
            staff=selected_staff,
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        )

        # Total appointments
        metrics['total_appointments'] = appointments.count()

        # Total revenue
        total_revenue = 0
        for appointment in appointments:
            if appointment.service:
                # Convert Decimal to float for JSON serialization
                total_revenue += float(appointment.service.price)
        metrics['total_revenue'] = total_revenue

        # Average rating
        reviews = Review.objects.filter(staff=selected_staff)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            # Convert Decimal to float for JSON serialization
            metrics['average_rating'] = float(avg_rating) if avg_rating is not None else 0
        else:
            metrics['average_rating'] = 0

        # Appointments by status
        status_counts = appointments.values('status').annotate(count=Count('id'))
        status_labels = []
        status_data = []

        for status in status_counts:
            status_labels.append(status['status'].title())
            status_data.append(status['count'])

        metrics['status_labels'] = json.dumps(status_labels)
        metrics['status_data'] = json.dumps(status_data)

        # Revenue by service
        service_revenue = {}
        for appointment in appointments:
            if appointment.service:
                service_name = appointment.service.name
                # Convert Decimal to float for JSON serialization
                price = float(appointment.service.price)
                if service_name in service_revenue:
                    service_revenue[service_name] += price
                else:
                    service_revenue[service_name] = price

        service_labels = list(service_revenue.keys())
        service_data = list(service_revenue.values())

        metrics['service_labels'] = json.dumps(service_labels)
        metrics['service_data'] = json.dumps(service_data)

        # Appointments over time
        time_data = {}
        current_date = start_date
        while current_date <= end_date:
            time_data[current_date.strftime('%Y-%m-%d')] = 0
            current_date += timedelta(days=1)

        for appointment in appointments:
            date_str = appointment.start_time.date().strftime('%Y-%m-%d')
            if date_str in time_data:
                time_data[date_str] += 1

        time_labels = list(time_data.keys())
        time_counts = list(time_data.values())

        metrics['time_labels'] = json.dumps(time_labels)
        metrics['time_data'] = json.dumps(time_counts)

        # Get recent reviews
        reviews = Review.objects.filter(staff=selected_staff).order_by('-created_at')[:5]
    else:
        reviews = []

    return render(request, 'admin_panel/staff_performance.html', {
        'title': 'Staff Performance',
        'staff_members': staff_members,
        'selected_staff': selected_staff,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'metrics': metrics,
        'reviews': reviews,
    })

@login_required
def admin_appointment_create(request):
    """
    View for creating a new appointment.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        # Get form data
        client_id = request.POST.get('client_id')
        service_id = request.POST.get('service_id')
        staff_id = request.POST.get('staff_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        notes = request.POST.get('notes', '')
        status = request.POST.get('status', 'pending')

        # Check if we're creating a new client
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Create new client if needed
        if first_name and last_name and email:
            # Generate a random password
            password = User.objects.make_random_password()

            # Create the user
            client = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone,
                role='client'
            )

            # Send welcome email with password
            # This would be implemented with an email notification system

            client_id = client.id

        # Validate required fields
        if not (client_id and service_id and staff_id and date_str and time_str):
            messages.error(request, "Please fill in all required fields.")
            return redirect('admin_panel:appointment_create')

        try:
            # Get related objects
            client = User.objects.get(id=client_id, role='client')
            service = Service.objects.get(id=service_id)
            staff = User.objects.get(id=staff_id, role='staff')

            # Parse date and time
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            start_time = timezone.make_aware(datetime.combine(date_obj, time_obj))

            # Calculate end time
            end_time = start_time + timedelta(minutes=service.duration)

            # Create the appointment
            appointment = Appointment.objects.create(
                client=client,
                service=service,
                staff=staff,
                start_time=start_time,
                end_time=end_time,
                status=status,
                notes=notes
            )

            # Log the creation
            UserLog.objects.create(
                user=request.user,
                action='create',
                entity_type='appointment',
                entity_id=appointment.id,
                details=f"Created appointment for {client.get_full_name()} on {start_time.strftime('%Y-%m-%d %H:%M')}"
            )

            # Create notifications
            Notification.objects.create(
                user=client,
                type='appointment',
                title='New Appointment',
                message=f"Your appointment for {service.name} has been scheduled for {start_time.strftime('%B %d, %Y')} at {start_time.strftime('%I:%M %p')} with {staff.get_full_name()}.",
                related_appointment=appointment
            )

            Notification.objects.create(
                user=staff,
                type='appointment',
                title='New Appointment Assigned',
                message=f"You have been assigned a new appointment for {service.name} with {client.get_full_name()} on {start_time.strftime('%B %d, %Y')} at {start_time.strftime('%I:%M %p')}.",
                related_appointment=appointment
            )

            # Show success message
            messages.success(request, "Appointment created successfully.")

            # Redirect to appointment detail
            return redirect('admin_panel:appointment_detail', appointment_id=appointment.id)

        except User.DoesNotExist:
            messages.error(request, "Client or staff member not found.")
        except Service.DoesNotExist:
            messages.error(request, "Service not found.")
        except Exception as e:
            messages.error(request, f"Error creating appointment: {str(e)}")

    # Get all clients, services, and staff members
    clients = User.objects.filter(role='client')
    services = Service.objects.filter(is_active=True)
    staff_members = User.objects.filter(role='staff', is_active=True)

    # Get today's date
    today = timezone.now().date()

    return render(request, 'admin_panel/appointment_create_modern.html', {
        'title': 'Create Appointment',
        'clients': clients,
        'services': services,
        'staff_members': staff_members,
        'today': today,
    })

@login_required
def admin_appointment_reschedule(request):
    """
    View for rescheduling an appointment via drag and drop.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        new_date = request.POST.get('new_date')
        new_time = request.POST.get('new_time')
        notify_client = request.POST.get('notify_client') == 'on'

        try:
            # Get the appointment
            appointment = Appointment.objects.get(id=appointment_id)

            # Create new datetime
            new_datetime_str = f"{new_date}T{new_time}"
            new_datetime = datetime.fromisoformat(new_datetime_str)

            # Update appointment
            old_datetime = appointment.start_time
            appointment.start_time = new_datetime
            appointment.save()

            # Log the change
            UserLog.objects.create(
                user=request.user,
                action='update',
                entity_type='appointment',
                entity_id=appointment.id,
                details=f"Rescheduled appointment from {old_datetime} to {new_datetime}"
            )

            # Notify client if requested
            if notify_client:
                # This would be implemented with an email notification system
                pass

            messages.success(request, "Appointment rescheduled successfully.")

            # Redirect to the appropriate view
            if 'week' in request.META.get('HTTP_REFERER', ''):
                # If coming from week view, redirect back to week view
                week_date = new_datetime.date()
                return redirect('admin_panel:calendar_week', year=week_date.year, month=week_date.month, day=week_date.day)
            else:
                # Otherwise redirect to month view
                return redirect('admin_panel:calendar')

        except Appointment.DoesNotExist:
            messages.error(request, "Appointment not found.")
        except Exception as e:
            messages.error(request, f"Error rescheduling appointment: {str(e)}")

    # If not POST or error occurred, redirect to calendar
    return redirect('admin_panel:calendar')

@login_required
def admin_calendar(request):
    """
    View for the calendar.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get current date
    today = timezone.now().date()
    year = today.year
    month = today.month

    # Get staff and service filters
    staff_id = request.GET.get('staff')
    service_id = request.GET.get('service')
    status = request.GET.get('status')

    # Get selected staff and service
    selected_staff = None
    selected_service = None

    if staff_id:
        try:
            selected_staff = User.objects.get(id=staff_id, role='staff')
        except User.DoesNotExist:
            pass

    if service_id:
        try:
            selected_service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            pass

    # Generate calendar data
    calendar_data = generate_calendar_data(year, month, selected_staff, selected_service, status)

    return render(request, 'admin_panel/calendar.html', {
        'title': 'Calendar',
        'calendar': calendar_data,
        'today': today,
        'staff_members': User.objects.filter(role='staff'),
        'services': Service.objects.all(),
        'selected_staff': selected_staff,
        'selected_service': selected_service,
    })

@login_required
def admin_calendar_month(request, year, month):
    """
    View for a specific month in the calendar.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get current date
    today = timezone.now().date()

    # Get staff and service filters
    staff_id = request.GET.get('staff')
    service_id = request.GET.get('service')
    status = request.GET.get('status')

    # Get selected staff and service
    selected_staff = None
    selected_service = None

    if staff_id:
        try:
            selected_staff = User.objects.get(id=staff_id, role='staff')
        except User.DoesNotExist:
            pass

    if service_id:
        try:
            selected_service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            pass

    # Generate calendar data
    calendar_data = generate_calendar_data(year, month, selected_staff, selected_service, status)

    return render(request, 'admin_panel/calendar.html', {
        'title': 'Calendar',
        'calendar': calendar_data,
        'today': today,
        'staff_members': User.objects.filter(role='staff'),
        'services': Service.objects.all(),
        'selected_staff': selected_staff,
        'selected_service': selected_service,
    })

@login_required
def admin_calendar_week(request, year, month, day):
    """
    View for a week in the calendar.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get current date
    today = timezone.now().date()

    # Create date object for the selected day
    try:
        selected_date = datetime(year, month, day).date()
    except ValueError:
        messages.error(request, "Invalid date.")
        return redirect('admin_panel:calendar')

    # Calculate the start of the week (Monday)
    week_start = selected_date - timedelta(days=selected_date.weekday())

    # Calculate the end of the week (Sunday)
    week_end = week_start + timedelta(days=6)

    # Calculate previous and next week
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)

    # Get staff and service filters
    staff_id = request.GET.get('staff')
    service_id = request.GET.get('service')
    status = request.GET.get('status')

    # Get selected staff and service
    selected_staff = None
    selected_service = None

    if staff_id:
        try:
            selected_staff = User.objects.get(id=staff_id, role='staff')
        except User.DoesNotExist:
            pass

    if service_id:
        try:
            selected_service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            pass

    # Get all appointments for the week
    appointments = Appointment.objects.filter(
        start_time__gte=datetime.combine(week_start, time.min),
        start_time__lt=datetime.combine(week_end + timedelta(days=1), time.min)
    ).order_by('start_time')

    # Apply filters
    if selected_staff:
        appointments = appointments.filter(staff=selected_staff)

    if selected_service:
        appointments = appointments.filter(service=selected_service)

    if status:
        appointments = appointments.filter(status=status)

    # Get holidays for the week
    holidays = Holiday.objects.filter(
        date__gte=week_start,
        date__lt=week_end + timedelta(days=1)
    )

    # Get recurring holidays (month and day match)
    recurring_holidays = Holiday.objects.filter(
        is_recurring=True
    )

    # Get business hours
    business_hours = BusinessHours.objects.all()

    # Generate hours for the day (8 AM to 8 PM)
    hours = []
    for hour in range(8, 21):
        hours.append(time(hour, 0))

    # Prepare days data
    days = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)

        # Get appointments for the day
        day_appointments = []
        for appointment in appointments:
            if appointment.start_time.date() == day_date:
                # Calculate position and height based on time and duration
                start_hour = appointment.start_time.hour
                start_minute = appointment.start_time.minute
                duration = appointment.service.duration

                # Calculate height (1 minute = 1 pixel)
                height = min(duration, 180)  # Cap at 3 hours for display

                day_appointments.append({
                    'id': appointment.id,
                    'client': appointment.client,
                    'staff': appointment.staff,
                    'service': appointment.service,
                    'start_time': appointment.start_time,
                    'status': appointment.status,
                    'duration': duration,
                    'start_hour': start_hour,
                    'start_minute': start_minute,
                    'height': height,
                })

        # Check if the day is a holiday
        holiday = None
        for h in holidays:
            if h.date == day_date:
                holiday = h.name
                break

        if not holiday:
            for h in recurring_holidays:
                if h.date.month == day_date.month and h.date.day == day_date.day:
                    holiday = h.name
                    break

        days.append({
            'date': day_date,
            'appointments': day_appointments,
            'holiday': holiday,
        })

    return render(request, 'admin_panel/calendar_week.html', {
        'title': f'Week Calendar - {week_start.strftime("%b %d")} to {week_end.strftime("%b %d, %Y")}',
        'week_start': week_start,
        'week_end': week_end,
        'prev_week': prev_week,
        'next_week': next_week,
        'days': days,
        'hours': hours,
        'today': today,
        'staff_members': User.objects.filter(role='staff'),
        'services': Service.objects.all(),
        'selected_staff': selected_staff,
        'selected_service': selected_service,
    })

@login_required
def admin_day_view(request, year, month, day):
    """
    View for a specific day in the calendar.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Create date object
    try:
        date = datetime(year, month, day).date()
    except ValueError:
        messages.error(request, "Invalid date.")
        return redirect('admin_panel:calendar')

    # Get previous and next day
    prev_day = date - timedelta(days=1)
    next_day = date + timedelta(days=1)

    # Get staff filter
    staff_id = request.GET.get('staff')
    selected_staff = None

    if staff_id:
        try:
            selected_staff = User.objects.get(id=staff_id, role='staff')
        except User.DoesNotExist:
            pass

    # Get appointments for the day
    appointments = Appointment.objects.filter(start_time__date=date).order_by('start_time')

    if selected_staff:
        appointments = appointments.filter(staff=selected_staff)

    # Check if the day is a holiday
    holiday = None
    try:
        holiday = Holiday.objects.get(date=date)
    except Holiday.DoesNotExist:
        # Check for recurring holidays (month and day match)
        try:
            holiday = Holiday.objects.get(date__month=date.month, date__day=date.day, is_recurring=True)
        except (Holiday.DoesNotExist, Holiday.MultipleObjectsReturned):
            pass

    # Get business hours for the day
    business_hours = None
    try:
        # Convert day of week (0 = Monday, 6 = Sunday)
        day_of_week = date.weekday()
        business_hours = BusinessHours.objects.get(day_of_week=day_of_week, is_open=True)
    except BusinessHours.DoesNotExist:
        pass

    # Generate hours and slots for the day
    hours = []
    slots = []

    if business_hours:
        # Generate hours from opening to closing time
        opening_hour = business_hours.opening_time.hour
        closing_hour = business_hours.closing_time.hour

        for hour in range(opening_hour, closing_hour + 1):
            hours.append(time(hour, 0))

        # Generate 30-minute slots
        for hour in range(opening_hour, closing_hour):
            for minute in [0, 30]:
                slot_time = time(hour, minute)
                # Make sure slot_datetime is timezone-aware
                slot_datetime = timezone.make_aware(datetime.combine(date, slot_time))

                # Check if slot is available
                is_available = True
                appointment = None

                for appt in appointments:
                    appt_start = appt.start_time
                    appt_end = appt_start + timedelta(minutes=appt.service.duration)

                    if appt_start <= slot_datetime < appt_end:
                        is_available = False
                        appointment = appt
                        break

                slots.append({
                    'hour': hour,
                    'minute': minute,
                    'time': slot_time,
                    'is_available': is_available,
                    'appointment': appointment,
                })

    return render(request, 'admin_panel/day_view.html', {
        'title': f'Day View - {date.strftime("%B %d, %Y")}',
        'date': date,
        'prev_day': prev_day,
        'next_day': next_day,
        'appointments': appointments,
        'holiday': holiday,
        'business_hours': business_hours,
        'hours': hours,
        'slots': slots,
        'staff_members': User.objects.filter(role='staff'),
        'selected_staff': selected_staff,
    })

def generate_calendar_data(year, month, selected_staff=None, selected_service=None, status=None):
    """
    Generate calendar data for the given month.
    """
    # Create calendar
    calendar = cal.monthcalendar(year, month)

    # Get month name
    month_name = cal.month_name[month]

    # Get previous and next month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Get all appointments for the month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()

    appointments = Appointment.objects.filter(
        start_time__gte=datetime.combine(start_date, time.min),
        start_time__lt=datetime.combine(end_date, time.min)
    ).order_by('start_time')

    # Apply filters
    if selected_staff:
        appointments = appointments.filter(staff=selected_staff)

    if selected_service:
        appointments = appointments.filter(service=selected_service)

    if status:
        appointments = appointments.filter(status=status)

    # Get holidays for the month
    holidays = Holiday.objects.filter(
        date__gte=start_date,
        date__lt=end_date
    )

    # Get recurring holidays (month and day match)
    recurring_holidays = Holiday.objects.filter(
        date__month=month,
        is_recurring=True
    )

    # Get business hours
    business_hours = BusinessHours.objects.all()

    # Prepare calendar data
    weeks = []
    for week in calendar:
        week_data = []
        for day in week:
            if day == 0:
                # Day outside the month
                week_data.append({
                    'day': '',
                    'current_month': False,
                    'date': None,
                    'appointments': [],
                    'holiday': None,
                    'is_available': False,
                })
            else:
                # Create date object
                date = datetime(year, month, day).date()

                # Get appointments for the day
                day_appointments = [a for a in appointments if a.start_time.date() == date]

                # Check if the day is a holiday
                holiday = None
                for h in holidays:
                    if h.date == date:
                        holiday = h.name
                        break

                if not holiday:
                    for h in recurring_holidays:
                        if h.date.day == day:
                            holiday = h.name
                            break

                # Check if the day is within business hours
                is_available = False
                day_of_week = date.weekday()  # 0 = Monday, 6 = Sunday
                for bh in business_hours:
                    if bh.day_of_week == day_of_week and bh.is_open:
                        is_available = True
                        break

                # If it's a holiday, it's not available
                if holiday:
                    is_available = False

                week_data.append({
                    'day': day,
                    'current_month': True,
                    'date': date,
                    'year': year,
                    'month': month,
                    'appointments': day_appointments,
                    'holiday': holiday,
                    'is_available': is_available,
                })

        weeks.append(week_data)

    return {
        'weeks': weeks,
        'month_name': month_name,
        'year': year,
        'month': month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }

@login_required
def admin_media(request):
    """
    View for managing media files.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all media files
    media_files = ServiceMedia.objects.all().order_by('-created_at')

    # Filter by media type if provided
    media_type = request.GET.get('type')
    if media_type:
        media_files = media_files.filter(media_type=media_type)

    # Filter by service if provided
    service_id = request.GET.get('service')
    if service_id:
        media_files = media_files.filter(service_id=service_id)

    return render(request, 'admin_panel/media.html', {
        'title': 'Media Management',
        'media_files': media_files,
        'services': Service.objects.all(),
    })

@login_required
def admin_media_gallery(request):
    """
    View for the media gallery.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all media files
    media_files = ServiceMedia.objects.all().order_by('-created_at')

    # Filter by media type if provided
    media_type = request.GET.get('type')
    if media_type:
        media_files = media_files.filter(media_type=media_type)

    # Filter by service if provided
    service_id = request.GET.get('service')
    if service_id:
        media_files = media_files.filter(service_id=service_id)

    return render(request, 'admin_panel/media_gallery_tailwind.html', {
        'title': 'Media Gallery',
        'media_files': media_files,
        'services': Service.objects.all(),
    })

@login_required
def admin_media_upload(request):
    """
    View for uploading media files.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        media_type = request.POST.get('media_type')
        service_id = request.POST.get('service')
        is_primary = request.POST.get('is_primary') == 'on'
        file = request.FILES.get('file')

        if not file:
            messages.error(request, "Please select a file to upload.")
            return redirect('admin_panel:media')

        # Create the media object
        media = ServiceMedia(
            media_type=media_type,
            file=file,
            is_primary=is_primary
        )

        # Associate with a service if provided
        if service_id:
            try:
                service = Service.objects.get(id=service_id)
                media.service = service

                # If this is set as primary, unset other primary media for this service
                if is_primary:
                    ServiceMedia.objects.filter(service=service, is_primary=True).update(is_primary=False)
            except Service.DoesNotExist:
                pass

        media.save()
        messages.success(request, "Media uploaded successfully.")

    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER', '')
    if 'gallery' in referer:
        return redirect('admin_panel:media_gallery')
    else:
        return redirect('admin_panel:media')

@login_required
def admin_media_upload_modal(request):
    """
    View for the upload modal (AJAX).
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        return JsonResponse({'error': "You don't have permission to access this page."}, status=403)

    # This is just a placeholder for the URL pattern
    # The actual modal is included in the gallery template
    return JsonResponse({'success': True})

@login_required
def admin_media_delete(request, media_id):
    """
    View for deleting a media file.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the media
    try:
        media = ServiceMedia.objects.get(id=media_id)
        media.delete()
        messages.success(request, "Media deleted successfully.")
    except ServiceMedia.DoesNotExist:
        messages.error(request, "Media not found.")

    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER', '')
    if 'gallery' in referer:
        return redirect('admin_panel:media_gallery')
    elif 'edit' in referer:
        return redirect('admin_panel:media')
    else:
        return redirect('admin_panel:media')

@login_required
def admin_media_set_primary(request, media_id):
    """
    View for setting a media file as primary for its service.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the media
    try:
        media = ServiceMedia.objects.get(id=media_id)

        if media.service:
            # Unset other primary media for this service
            ServiceMedia.objects.filter(service=media.service, is_primary=True).update(is_primary=False)

            # Set this media as primary
            media.is_primary = True
            media.save()

            messages.success(request, "Media set as primary successfully.")
        else:
            messages.error(request, "This media is not associated with any service.")
    except ServiceMedia.DoesNotExist:
        messages.error(request, "Media not found.")

    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER', '')
    if 'gallery' in referer:
        return redirect('admin_panel:media_gallery')
    elif 'edit' in referer:
        return redirect('admin_panel:media_edit', media_id=media_id)
    else:
        return redirect('admin_panel:media')

@login_required
def admin_media_edit(request, media_id):
    """
    View for editing a media file.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the media
    try:
        media = ServiceMedia.objects.get(id=media_id)

        # Only images can be edited
        if media.media_type != 'image':
            messages.error(request, "Only images can be edited.")
            return redirect('admin_panel:media')

        return render(request, 'admin_panel/media_edit.html', {
            'title': 'Edit Image',
            'media': media,
            'services': Service.objects.all(),
        })
    except ServiceMedia.DoesNotExist:
        messages.error(request, "Media not found.")
        return redirect('admin_panel:media')

@login_required
def admin_media_edit_save(request, media_id):
    """
    View for saving edited media.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method != 'POST':
        return redirect('admin_panel:media_edit', media_id=media_id)

    # Get the media
    try:
        media = ServiceMedia.objects.get(id=media_id)

        # Only images can be edited
        if media.media_type != 'image':
            messages.error(request, "Only images can be edited.")
            return redirect('admin_panel:media')

        # Get form data
        crop_data = request.POST.get('crop_data')
        rotate_angle = int(request.POST.get('rotate_angle', 0))
        flip_horizontal = request.POST.get('flip_horizontal') == '1'
        flip_vertical = request.POST.get('flip_vertical') == '1'
        brightness = int(request.POST.get('brightness', 0))
        contrast = int(request.POST.get('contrast', 0))
        service_id = request.POST.get('service')
        is_primary = request.POST.get('is_primary') == 'on'

        # Update service and primary status
        if service_id:
            try:
                service = Service.objects.get(id=service_id)
                media.service = service

                # If this is set as primary, unset other primary media for this service
                if is_primary and not media.is_primary:
                    ServiceMedia.objects.filter(service=service, is_primary=True).update(is_primary=False)
                    media.is_primary = True
            except Service.DoesNotExist:
                pass
        else:
            media.service = None
            media.is_primary = False

        # Process image if there are edits
        if crop_data or rotate_angle != 0 or flip_horizontal or flip_vertical or brightness != 0 or contrast != 0:
            # Open the image
            img = Image.open(media.file.path)

            # Apply rotation
            if rotate_angle != 0:
                img = img.rotate(-rotate_angle, expand=True)

            # Apply flips
            if flip_horizontal:
                img = ImageOps.mirror(img)

            if flip_vertical:
                img = ImageOps.flip(img)

            # Apply crop if provided
            if crop_data:
                try:
                    crop_data = json.loads(crop_data)
                    x = int(crop_data.get('x', 0))
                    y = int(crop_data.get('y', 0))
                    width = int(crop_data.get('width', img.width))
                    height = int(crop_data.get('height', img.height))

                    # Ensure crop dimensions are valid
                    if width > 0 and height > 0:
                        img = img.crop((x, y, x + width, y + height))
                except (ValueError, json.JSONDecodeError):
                    pass

            # Apply brightness
            if brightness != 0:
                factor = 1.0 + (brightness / 100.0)
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(factor)

            # Apply contrast
            if contrast != 0:
                factor = 1.0 + (contrast / 100.0)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(factor)

            # Save the edited image
            img.save(media.file.path)

        # Save the media object
        media.save()

        messages.success(request, "Image updated successfully.")
        return redirect('admin_panel:media_edit', media_id=media_id)

    except ServiceMedia.DoesNotExist:
        messages.error(request, "Media not found.")
        return redirect('admin_panel:media')
    except Exception as e:
        messages.error(request, f"Error updating image: {str(e)}")
        return redirect('admin_panel:media_edit', media_id=media_id)

@login_required
def admin_pending_appointments(request):
    """
    View for admins to see all pending appointment requests.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Handle bulk approve action
    if request.method == 'POST' and 'bulk_approve' in request.POST:
        appointment_ids = request.POST.getlist('appointment_ids')
        date_filter = request.POST.get('date_filter')

        if appointment_ids:
            # Approve selected appointments
            approved_count = approve_appointments(request, appointment_ids)
            messages.success(request, f"{approved_count} appointments have been approved and staff assigned.")
        elif date_filter:
            # Approve all appointments for a specific date
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                appointments_to_approve = Appointment.objects.filter(
                    status='pending_review',
                    start_time__date=filter_date
                )
                appointment_ids = list(appointments_to_approve.values_list('id', flat=True))
                approved_count = approve_appointments(request, appointment_ids)
                messages.success(request, f"{approved_count} appointments for {filter_date.strftime('%B %d, %Y')} have been approved.")
            except ValueError:
                messages.error(request, "Invalid date format.")
        else:
            messages.error(request, "No appointments selected for approval.")

        return redirect('admin_panel:pending_appointments')

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

    # Get all staff members for assignment
    staff_members = User.objects.filter(role='staff', is_active=True)

    # Group appointments by date for easier viewing
    appointments_by_date = {}
    for appointment in pending_appointments:
        date = appointment.start_time.date()
        if date not in appointments_by_date:
            appointments_by_date[date] = []
        appointments_by_date[date].append(appointment)

    # Sort dates
    sorted_dates = sorted(appointments_by_date.keys())

    return render(request, 'admin_panel/appointments/pending_list_tailwind.html', {
        'appointments': pending_appointments,
        'appointments_by_date': appointments_by_date,
        'sorted_dates': sorted_dates,
        'title': 'Pending Appointment Requests',
        'today': today,
        'tomorrow': tomorrow,
        'today_count': today_count,
        'oldest_request': oldest_request,
        'services': services,
        'staff_members': staff_members,
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

    # Get all active staff members
    staff_members = User.objects.filter(role='staff', is_active=True)

    # Get the day of the week for the appointment
    day_of_week = appointment.start_time.weekday()

    # Filter staff members who are working on this day
    available_staff = []
    all_staff = list(staff_members)

    for staff in staff_members:
        try:
            # Check if the staff member is working on this day
            schedule = Schedule.objects.get(staff=staff, day_of_week=day_of_week, is_working=True)

            # Check if the appointment is within the staff's working hours
            staff_start = timezone.make_aware(datetime.combine(appointment.start_time.date(), schedule.start_time))
            staff_end = timezone.make_aware(datetime.combine(appointment.start_time.date(), schedule.end_time))

            if appointment.start_time >= staff_start and appointment.end_time <= staff_end:
                # Check if the staff member has any overlapping appointments
                overlapping_appointments = Appointment.objects.filter(
                    staff=staff,
                    start_time__lt=appointment.end_time,
                    end_time__gt=appointment.start_time,
                    status__in=['pending', 'confirmed']
                )

                if not overlapping_appointments.exists():
                    available_staff.append(staff)
        except Schedule.DoesNotExist:
            # Staff member is not working on this day
            continue

    # Add appointment counts for each staff member
    for staff in all_staff:
        staff.appointments_today = Appointment.objects.filter(
            staff=staff,
            start_time__date=appointment.start_time.date()
        ).count()

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

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        new_time = request.POST.get('new_time')

        changes = {}

        # Assign staff if provided
        if staff_id:
            staff = get_object_or_404(User, id=staff_id, role='staff')
            appointment.staff = staff
            changes['staff'] = staff.get_full_name()

        # Update time if provided
        if new_time:
            try:
                # Parse the time string (format: HH:MM)
                hour, minute = map(int, new_time.split(':'))
                time_obj = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()

                # Create new datetime objects
                new_start = timezone.make_aware(datetime.combine(appointment.start_time.date(), time_obj))
                new_end = new_start + timedelta(minutes=appointment.service.duration)

                # Update the appointment times
                old_time = appointment.start_time.strftime('%I:%M %p')
                appointment.start_time = new_start
                appointment.end_time = new_end
                changes['time'] = f"from {old_time} to {new_start.strftime('%I:%M %p')}"
            except (ValueError, TypeError, IndexError):
                messages.error(request, "Invalid time format.")
                return redirect('admin_panel:review_appointment', appointment_id=appointment.id)

        # Update status to confirmed
        appointment.status = 'confirmed'
        changes['status'] = 'Confirmed'

        # Save the appointment
        appointment.save()

        # Create notifications
        Notification.objects.create(
            user=appointment.client,
            type='appointment',
            title='Appointment Confirmed',
            message=f"Your appointment for {appointment.service.name} has been confirmed for {appointment.start_time.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')} with {appointment.staff.get_full_name()}.",
            related_appointment=appointment
        )

        Notification.objects.create(
            user=appointment.staff,
            type='appointment',
            title='New Appointment Assigned',
            message=f"You have been assigned a new appointment for {appointment.service.name} with {appointment.client.get_full_name()} on {appointment.start_time.strftime('%B %d, %Y')} at {appointment.start_time.strftime('%I:%M %p')}.",
            related_appointment=appointment
        )

        # Send email notifications
        from apps.notifications.email_utils import send_appointment_update, send_staff_new_appointment
        send_appointment_update(appointment, changes)
        send_staff_new_appointment(appointment)

        messages.success(request, "Appointment has been confirmed and staff assigned.")
        return redirect('admin_panel:pending_appointments')

    return render(request, 'admin_panel/appointments/review_tailwind.html', {
        'appointment': appointment,
        'available_staff': available_staff,
        'all_staff': all_staff,
        'title': 'Review Appointment Request',
        'today': today,
        'tomorrow': tomorrow,
        'day_appointments': formatted_appointments,
        'appointment_top': appointment_top,
        'appointment_height': appointment_height,
        'hours': hours,
    })
