from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from apps.core.models import Holiday
from .models import UserLog
from .tailwind_forms import HolidayForm

@login_required
def admin_holiday_create_modern(request):
    """
    Modern view for creating a new holiday.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            holiday = form.save()

            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='create',
                entity_type='holiday',
                entity_id=holiday.id,
                details=f"Created new holiday: {holiday.name} on {holiday.date.strftime('%Y-%m-%d')}"
            )

            messages.success(request, "Holiday created successfully.")
            return redirect('admin_panel:holidays')
    else:
        form = HolidayForm()

    # Get upcoming holidays for display
    today = timezone.now().date()
    upcoming_holidays = Holiday.objects.filter(date__gte=today).order_by('date')[:5]

    return render(request, 'admin_panel/holiday_create_modern.html', {
        'title': 'Create Holiday',
        'form': form,
        'upcoming_holidays': upcoming_holidays,
    })

@login_required
def admin_holiday_edit_modern(request, holiday_id):
    """
    Modern view for editing a holiday.
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
            updated_holiday = form.save()

            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='update',
                entity_type='holiday',
                entity_id=holiday.id,
                details=f"Updated holiday: {updated_holiday.name} on {updated_holiday.date.strftime('%Y-%m-%d')}"
            )

            messages.success(request, "Holiday updated successfully.")
            return redirect('admin_panel:holidays')
    else:
        form = HolidayForm(instance=holiday)

    # Get upcoming holidays for display
    today = timezone.now().date()
    upcoming_holidays = Holiday.objects.filter(date__gte=today).exclude(id=holiday_id).order_by('date')[:5]

    return render(request, 'admin_panel/holiday_edit_modern.html', {
        'title': 'Edit Holiday',
        'form': form,
        'holiday': holiday,
        'upcoming_holidays': upcoming_holidays,
    })
