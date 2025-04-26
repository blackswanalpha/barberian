from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum
import json
from datetime import timedelta, datetime

from apps.core.models import User
from apps.appointments.models import Appointment
from apps.services.models import Service, Category
from apps.admin_panel.models import UserLog
from apps.staff.models import StaffSettings

@login_required
def admin_dashboard_modern(request):
    """
    Modern dashboard view with redesigned UI.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get today's date
    today = timezone.now().date()

    # Get total appointments
    total_appointments = Appointment.objects.count()

    # Get appointments from last month for growth calculation
    last_month_start = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_start.replace(day=1)
    last_month_end = today.replace(day=1) - timedelta(days=1)

    last_month_appointments = Appointment.objects.filter(
        created_at__date__gte=last_month_start,
        created_at__date__lte=last_month_end
    ).count()

    current_month_appointments = Appointment.objects.filter(
        created_at__date__gte=today.replace(day=1),
        created_at__date__lte=today
    ).count()

    # Calculate growth
    if last_month_appointments > 0:
        appointment_growth = round(((current_month_appointments - last_month_appointments) / last_month_appointments) * 100)
    else:
        appointment_growth = 100 if current_month_appointments > 0 else 0

    # Get total revenue
    total_revenue = Appointment.objects.filter(status='completed').aggregate(
        total=Sum('service__price')
    )['total'] or 0

    # Calculate revenue growth
    last_month_revenue = Appointment.objects.filter(
        status='completed',
        start_time__date__gte=last_month_start,
        start_time__date__lte=last_month_end
    ).aggregate(total=Sum('service__price'))['total'] or 0

    current_month_revenue = Appointment.objects.filter(
        status='completed',
        start_time__date__gte=today.replace(day=1),
        start_time__date__lte=today
    ).aggregate(total=Sum('service__price'))['total'] or 0

    if last_month_revenue > 0:
        revenue_growth = round(((current_month_revenue - last_month_revenue) / last_month_revenue) * 100)
    else:
        revenue_growth = 100 if current_month_revenue > 0 else 0

    # Get total clients
    total_clients = User.objects.filter(role='client').count()

    # Calculate client growth
    last_month_clients = User.objects.filter(
        role='client',
        date_joined__date__gte=last_month_start,
        date_joined__date__lte=last_month_end
    ).count()

    current_month_clients = User.objects.filter(
        role='client',
        date_joined__date__gte=today.replace(day=1),
        date_joined__date__lte=today
    ).count()

    if last_month_clients > 0:
        client_growth = round(((current_month_clients - last_month_clients) / last_month_clients) * 100)
    else:
        client_growth = 100 if current_month_clients > 0 else 0

    # Get pending appointments count
    pending_count = Appointment.objects.filter(status='pending').count()

    # Get recent appointments
    recent_appointments = Appointment.objects.select_related('client', 'service').order_by('-created_at')[:5]

    # Get today's appointments
    todays_appointments = Appointment.objects.select_related('client', 'service').filter(
        start_time__date=today
    ).order_by('start_time')

    # Get popular services
    popular_services = Service.objects.annotate(
        booking_count=Count('appointments')
    ).order_by('-booking_count')[:5]

    # Get recent activity logs
    recent_logs = UserLog.objects.select_related('user').order_by('-created_at')[:5]

    # Get appointments data for chart
    # Last 7 days
    appointments_data = []
    appointments_labels = []

    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = Appointment.objects.filter(start_time__date=date).count()
        appointments_data.append(count)
        appointments_labels.append(date.strftime('%a'))

    return render(request, 'admin_panel/dashboard_modern.html', {
        'total_appointments': total_appointments,
        'appointment_growth': appointment_growth,
        'total_revenue': total_revenue,
        'revenue_growth': revenue_growth,
        'total_clients': total_clients,
        'client_growth': client_growth,
        'pending_count': pending_count,
        'recent_appointments': recent_appointments,
        'today': today,
        'todays_appointments': todays_appointments,
        'popular_services': popular_services,
        'recent_logs': recent_logs,
        'appointments_data': json.dumps(appointments_data),
        'appointments_labels': json.dumps(appointments_labels),
    })

@login_required
def admin_appointments_modern(request):
    """
    Modern appointments view with redesigned UI.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all appointments
    appointments = Appointment.objects.select_related('client', 'service', 'staff').order_by('-start_time')

    return render(request, 'admin_panel/appointments_modern.html', {
        'title': 'Appointments',
        'appointments': appointments,
    })

@login_required
def admin_staff_modern(request):
    """
    Modern staff view with redesigned UI.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all staff members
    staff_members = User.objects.filter(role='staff').order_by('first_name')

    return render(request, 'admin_panel/staff_modern.html', {
        'title': 'Staff Management',
        'staff_members': staff_members,
    })

@login_required
def admin_services_modern(request):
    """
    Modern services view with redesigned UI.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all services
    services = Service.objects.select_related('category').order_by('category__name', 'name')

    # Get all categories for filtering
    categories = Category.objects.all().order_by('name')

    return render(request, 'admin_panel/services_modern.html', {
        'title': 'Services',
        'services': services,
        'categories': categories,
    })

@login_required
def admin_pending_appointments_modern(request):
    """
    Modern pending appointments view with enhanced features.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Handle bulk approve action
    if request.method == 'POST' and 'bulk_approve' in request.POST:
        from apps.admin_panel.views import approve_appointments
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

        return redirect('admin_panel:pending_appointments_modern')

    # Get all pending review appointments
    pending_appointments = Appointment.objects.filter(
        status='pending_review'
    ).select_related('client', 'service').order_by('start_time')

    # Get all services for filtering
    services = Service.objects.all().order_by('name')

    # Get all staff members for assignment
    staff_members = User.objects.filter(role='staff', is_active=True).order_by('first_name')

    # Get today's date for highlighting
    today = timezone.localtime().date()
    tomorrow = today + timedelta(days=1)

    # Get today's pending count
    today_count = pending_appointments.filter(start_time__date=today).count()

    # Get oldest request date
    oldest_request = None
    if pending_appointments.exists():
        oldest_request = pending_appointments.first().start_time.date()

    # Group appointments by date for easier viewing
    appointments_by_date = {}
    formatted_dates = {}  # For display in the template

    for appointment in pending_appointments:
        date = appointment.start_time.date()
        date_str = date.strftime('%Y-%m-%d')  # Convert date to string for template

        if date_str not in appointments_by_date:
            appointments_by_date[date_str] = []
            formatted_dates[date_str] = date.strftime('%A, %B %d, %Y')  # Format for display

        appointments_by_date[date_str].append(appointment)

    # Sort dates
    sorted_dates = sorted(appointments_by_date.keys(), key=lambda x: datetime.strptime(x, '%Y-%m-%d').date())

    return render(request, 'admin_panel/appointments/pending_list_modern.html', {
        'title': 'Pending Appointment Requests',
        'appointments': pending_appointments,
        'appointments_by_date': appointments_by_date,
        'sorted_dates': sorted_dates,
        'formatted_dates': formatted_dates,
        'services': services,
        'staff_members': staff_members,
        'today': today,
        'tomorrow': tomorrow,
        'today_count': today_count,
        'oldest_request': oldest_request,
        'today_str': today.strftime('%Y-%m-%d'),
        'tomorrow_str': tomorrow.strftime('%Y-%m-%d'),
    })
