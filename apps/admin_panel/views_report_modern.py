from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
import json
from datetime import datetime, timedelta

from apps.core.models import User
from apps.appointments.models import Appointment
from apps.payments.models import Payment, Invoice
from .models import Report, ReportExport, UserLog
from .tailwind_forms import ReportForm

@login_required
def admin_report_create_modern(request):
    """
    Modern view for creating a new report.
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

            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='create',
                entity_type='report',
                entity_id=report.id,
                details=f"Created new report: {report.name} ({report.get_type_display()})"
            )

            messages.success(request, "Report created successfully.")
            return redirect('admin_panel:reports')
    else:
        form = ReportForm()

    return render(request, 'admin_panel/report_form_modern.html', {
        'title': 'Create Report',
        'form': form,
    })

@login_required
def admin_report_detail_modern(request, report_id):
    """
    Modern view for viewing a report.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the report
    report = get_object_or_404(Report, id=report_id)

    # Get filter parameters
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')

    # Set default date range if not provided (last 30 days)
    today = timezone.now().date()
    if date_from_str:
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
    else:
        date_from = today - timedelta(days=30)

    if date_to_str:
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
    else:
        date_to = today

    # Initialize variables
    report_data = []
    chart_labels = []
    chart_data = []

    # Generate report based on type
    if report.type == 'appointments':
        # Get additional filters
        status = request.GET.get('status', '')

        # Base query
        appointments = Appointment.objects.filter(
            start_time__date__gte=date_from,
            start_time__date__lte=date_to
        ).order_by('-start_time')

        # Apply status filter if provided
        if status:
            appointments = appointments.filter(status=status)

        # Calculate summary statistics
        total_appointments = appointments.count()
        completed_appointments = appointments.filter(status='completed').count()
        cancelled_appointments = appointments.filter(Q(status='cancelled') | Q(status='no_show')).count()

        # Prepare data for table
        for appointment in appointments:
            report_data.append({
                'date': appointment.start_time.strftime('%Y-%m-%d %H:%M'),
                'client': appointment.client.get_full_name(),
                'service': appointment.service.name,
                'staff': appointment.staff.get_full_name() if appointment.staff else 'Unassigned',
                'status': appointment.status,
                'status_display': appointment.get_status_display(),
                'duration': appointment.service.duration,
                'price': appointment.service.price
            })

        # Prepare data for chart (appointments by day)
        date_range = (date_to - date_from).days + 1
        for i in range(date_range):
            date = date_from + timedelta(days=i)
            chart_labels.append(date.strftime('%Y-%m-%d'))

            count = appointments.filter(start_time__date=date).count()
            chart_data.append(count)

        # Render the template
        return render(request, 'admin_panel/report_detail_modern.html', {
            'title': f'Report: {report.name}',
            'report': report,
            'date_from': date_from,
            'date_to': date_to,
            'status': status,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'report_data': report_data,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
        })

    elif report.type == 'revenue':
        # Get additional filters
        payment_method = request.GET.get('payment_method', '')

        # Base query
        payments = Payment.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
            status='completed'
        ).order_by('-created_at')

        # Apply payment method filter if provided
        if payment_method:
            payments = payments.filter(payment_method=payment_method)

        # Calculate summary statistics
        total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        total_transactions = payments.count()
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0

        # Prepare data for table
        for payment in payments:
            try:
                invoice = Invoice.objects.get(payment=payment)
                services = ", ".join([item.service.name for item in invoice.invoiceitem_set.all()])
                invoice_number = invoice.invoice_number
            except Invoice.DoesNotExist:
                services = "N/A"
                invoice_number = "N/A"

            report_data.append({
                'date': payment.created_at.strftime('%Y-%m-%d %H:%M'),
                'invoice_number': invoice_number,
                'client': payment.client.get_full_name(),
                'services': services,
                'payment_method': payment.get_payment_method_display(),
                'amount': payment.amount
            })

        # Prepare data for chart (revenue by day)
        date_range = (date_to - date_from).days + 1
        for i in range(date_range):
            date = date_from + timedelta(days=i)
            chart_labels.append(date.strftime('%Y-%m-%d'))

            daily_revenue = payments.filter(created_at__date=date).aggregate(Sum('amount'))['amount__sum'] or 0
            chart_data.append(daily_revenue)

        # Render the template
        return render(request, 'admin_panel/report_detail_modern.html', {
            'title': f'Report: {report.name}',
            'report': report,
            'date_from': date_from,
            'date_to': date_to,
            'payment_method': payment_method,
            'total_revenue': total_revenue,
            'total_transactions': total_transactions,
            'avg_transaction': avg_transaction,
            'report_data': report_data,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
        })

    elif report.type == 'staff':
        # Get additional filters
        staff_id = request.GET.get('staff_id', '')

        # Get all staff members
        staff_members = User.objects.filter(role='staff')

        # Base query for appointments
        appointments = Appointment.objects.filter(
            start_time__date__gte=date_from,
            start_time__date__lte=date_to
        )

        # Apply staff filter if provided
        if staff_id:
            appointments = appointments.filter(staff_id=staff_id)
            staff_members = staff_members.filter(id=staff_id)

        # Prepare data for table
        for staff in staff_members:
            staff_appointments = appointments.filter(staff=staff)
            completed = staff_appointments.filter(status='completed').count()
            cancelled = staff_appointments.filter(Q(status='cancelled') | Q(status='no_show')).count()

            # Calculate revenue from completed appointments
            revenue = 0
            for appointment in staff_appointments.filter(status='completed'):
                revenue += appointment.service.price

            # Calculate average duration
            avg_duration = staff_appointments.aggregate(Avg('service__duration'))['service__duration__avg'] or 0

            report_data.append({
                'staff': staff.get_full_name(),
                'appointments': staff_appointments.count(),
                'completed': completed,
                'cancelled': cancelled,
                'revenue': revenue,
                'avg_duration': round(avg_duration, 0)
            })

        # Calculate summary statistics
        total_appointments = appointments.count()
        total_revenue = sum(item['revenue'] for item in report_data)
        avg_duration = appointments.aggregate(Avg('service__duration'))['service__duration__avg'] or 0

        # Prepare data for chart (appointments by staff)
        for staff_data in report_data:
            chart_labels.append(staff_data['staff'])
            chart_data.append(staff_data['appointments'])

        # Render the template
        return render(request, 'admin_panel/report_detail_modern.html', {
            'title': f'Report: {report.name}',
            'report': report,
            'date_from': date_from,
            'date_to': date_to,
            'staff_id': staff_id,
            'staff_members': staff_members,
            'total_appointments': total_appointments,
            'total_revenue': total_revenue,
            'avg_duration': round(avg_duration, 0),
            'report_data': report_data,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
        })

    # Default case - unknown report type
    messages.error(request, "Unknown report type.")
    return redirect('admin_panel:reports')
