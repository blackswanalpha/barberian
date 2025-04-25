from datetime import datetime, timedelta, date
from calendar import monthrange
from django.utils import timezone
from django.db.models import Q

from .models import Appointment
from apps.core.models import BusinessHours, Holiday
from apps.staff.models import Schedule

def get_month_calendar(year, month, staff=None):
    """
    Generate a calendar for the specified month.

    Args:
        year (int): The year
        month (int): The month (1-12)
        staff (User, optional): The staff member to filter appointments for

    Returns:
        dict: A dictionary containing calendar information
    """
    # Get the first day of the month
    first_day = date(year, month, 1)

    # Get the number of days in the month
    _, num_days = monthrange(year, month)

    # Get the day of the week for the first day (0 = Monday, 6 = Sunday)
    first_day_weekday = first_day.weekday()

    # Adjust for Sunday as the first day of the week
    if first_day_weekday == 6:
        first_day_weekday = 0
    else:
        first_day_weekday += 1

    # Calculate the number of days from the previous month to show
    prev_month_days = first_day_weekday

    # Calculate the number of days from the next month to show
    next_month_days = (7 - ((prev_month_days + num_days) % 7)) % 7

    # Get the previous month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Get the next month
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Get the number of days in the previous month
    _, prev_month_num_days = monthrange(prev_year, prev_month)

    # Generate the calendar days
    calendar_days = []

    # Add days from the previous month
    for i in range(prev_month_days):
        day = prev_month_num_days - prev_month_days + i + 1
        calendar_days.append({
            'day': day,
            'month': prev_month,
            'year': prev_year,
            'current_month': False,
            'date': date(prev_year, prev_month, day)
        })

    # Add days from the current month
    for day in range(1, num_days + 1):
        calendar_days.append({
            'day': day,
            'month': month,
            'year': year,
            'current_month': True,
            'date': date(year, month, day)
        })

    # Add days from the next month
    for day in range(1, next_month_days + 1):
        calendar_days.append({
            'day': day,
            'month': next_month,
            'year': next_year,
            'current_month': False,
            'date': date(next_year, next_month, day)
        })

    # Get holidays
    holidays = Holiday.objects.all()
    holiday_dates = {}

    for holiday in holidays:
        if holiday.is_recurring:
            # For recurring holidays, check if the month matches
            if holiday.date.month == month:
                # Create a date object for this year
                holiday_date = date(year, holiday.date.month, holiday.date.day)
                holiday_dates[holiday_date] = holiday.name
        else:
            # For non-recurring holidays, check if the date is in the calendar
            if holiday.date.year == year and holiday.date.month == month:
                holiday_dates[holiday.date] = holiday.name

    # Get business hours
    business_hours = {}
    for bh in BusinessHours.objects.all():
        business_hours[bh.day_of_week] = {
            'is_open': bh.is_open,
            'opening_time': bh.opening_time,
            'closing_time': bh.closing_time
        }

    # Get staff schedule if provided
    staff_schedule = {}
    if staff:
        for schedule in Schedule.objects.filter(staff=staff):
            staff_schedule[schedule.day_of_week] = {
                'is_working': schedule.is_working,
                'start_time': schedule.start_time,
                'end_time': schedule.end_time
            }

    # Get appointments
    start_date = calendar_days[0]['date']
    end_date = calendar_days[-1]['date'] + timedelta(days=1)  # Add one day to include the end date

    # Create timezone-aware datetime objects
    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.min.time()))

    appointments_query = Appointment.objects.filter(
        start_time__gte=start_datetime,
        start_time__lt=end_datetime
    )

    if staff:
        appointments_query = appointments_query.filter(staff=staff)

    appointments = appointments_query.order_by('start_time')

    # Group appointments by date
    appointments_by_date = {}
    for appointment in appointments:
        appointment_date = appointment.start_time.date()
        if appointment_date not in appointments_by_date:
            appointments_by_date[appointment_date] = []
        appointments_by_date[appointment_date].append(appointment)

    # Add appointments, holidays, and business hours to calendar days
    for day in calendar_days:
        day_date = day['date']

        # Add appointments
        day['appointments'] = appointments_by_date.get(day_date, [])

        # Add holiday
        day['holiday'] = holiday_dates.get(day_date)

        # Add business hours
        day_of_week = day_date.weekday()
        day['business_hours'] = business_hours.get(day_of_week, {
            'is_open': False,
            'opening_time': None,
            'closing_time': None
        })

        # Add staff schedule
        if staff:
            day['staff_schedule'] = staff_schedule.get(day_of_week, {
                'is_working': False,
                'start_time': None,
                'end_time': None
            })

        # Check if the day is available for booking
        day['is_available'] = (
            day['current_month'] and
            day_date >= timezone.now().date() and
            day['business_hours']['is_open'] and
            not day['holiday'] and
            (not staff or day.get('staff_schedule', {}).get('is_working', False))
        )

    # Create weeks
    weeks = []
    for i in range(0, len(calendar_days), 7):
        weeks.append(calendar_days[i:i+7])

    return {
        'year': year,
        'month': month,
        'month_name': datetime(year, month, 1).strftime('%B'),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'weeks': weeks,
        'calendar_days': calendar_days,
        'holidays': holiday_dates,
        'business_hours': business_hours,
        'staff_schedule': staff_schedule if staff else None,
        'appointments_by_date': appointments_by_date
    }

def get_day_schedule(date_obj, staff=None):
    """
    Get the schedule for a specific day.

    Args:
        date_obj (date): The date to get the schedule for
        staff (User, optional): The staff member to filter appointments for

    Returns:
        dict: A dictionary containing schedule information
    """
    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = date_obj.weekday()

    # Get business hours for this day
    try:
        business_hours = BusinessHours.objects.get(day_of_week=day_of_week)
        is_open = business_hours.is_open
        opening_time = business_hours.opening_time
        closing_time = business_hours.closing_time
    except BusinessHours.DoesNotExist:
        is_open = False
        opening_time = None
        closing_time = None

    # Check if this day is a holiday
    is_holiday = Holiday.objects.filter(
        Q(date=date_obj) |
        Q(is_recurring=True, date__month=date_obj.month, date__day=date_obj.day)
    ).exists()

    # Get staff schedule if provided
    staff_schedule = None
    if staff:
        try:
            schedule = Schedule.objects.get(staff=staff, day_of_week=day_of_week)
            staff_schedule = {
                'is_working': schedule.is_working,
                'start_time': schedule.start_time,
                'end_time': schedule.end_time
            }
        except Schedule.DoesNotExist:
            staff_schedule = {
                'is_working': False,
                'start_time': None,
                'end_time': None
            }

    # Get appointments for this day
    # Create timezone-aware datetime objects
    start_datetime = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(date_obj + timedelta(days=1), datetime.min.time()))

    appointments_query = Appointment.objects.filter(
        start_time__gte=start_datetime,
        start_time__lt=end_datetime
    )

    if staff:
        appointments_query = appointments_query.filter(staff=staff)

    appointments = appointments_query.order_by('start_time')

    # Check if the day is available for booking
    is_available = (
        is_open and
        not is_holiday and
        date_obj >= timezone.now().date() and
        (not staff or (staff_schedule and staff_schedule['is_working']))
    )

    return {
        'date': date_obj,
        'day_of_week': day_of_week,
        'day_name': date_obj.strftime('%A'),
        'is_open': is_open,
        'opening_time': opening_time,
        'closing_time': closing_time,
        'is_holiday': is_holiday,
        'staff_schedule': staff_schedule,
        'appointments': appointments,
        'is_available': is_available
    }

def get_time_slots(date_obj, service, staff=None):
    """
    Get available time slots for a specific day.

    Args:
        date_obj (date): The date to get time slots for
        service (Service): The service to book
        staff (User, optional): The staff member to filter time slots for

    Returns:
        list: A list of available time slots
    """
    # Get the schedule for this day
    schedule = get_day_schedule(date_obj, staff)

    # If the day is not available, return an empty list
    if not schedule['is_available']:
        return []

    # Get the service duration in minutes
    duration = service.duration

    # Determine the start and end times
    if staff and schedule['staff_schedule']:
        start_time = schedule['staff_schedule']['start_time']
        end_time = schedule['staff_schedule']['end_time']
    else:
        start_time = schedule['opening_time']
        end_time = schedule['closing_time']

    # If no start or end time, return an empty list
    if not start_time or not end_time:
        return []

    # Convert to timezone-aware datetime objects
    start_datetime = timezone.make_aware(datetime.combine(date_obj, start_time))
    end_datetime = timezone.make_aware(datetime.combine(date_obj, end_time))

    # Adjust for current time if the date is today
    if date_obj == timezone.now().date():
        current_time = timezone.now()
        # Round up to the nearest 15 minutes
        minutes = current_time.minute
        if minutes % 15 > 0:
            minutes = minutes + (15 - minutes % 15)
        current_time = current_time.replace(minute=minutes, second=0, microsecond=0)

        if current_time > start_datetime:
            start_datetime = current_time

    # Generate time slots in 15-minute intervals
    time_slots = []
    current_slot = start_datetime

    while current_slot + timedelta(minutes=duration) <= end_datetime:
        # Check if this slot conflicts with any existing appointments
        slot_end = current_slot + timedelta(minutes=duration)
        conflict = False

        for appointment in schedule['appointments']:
            # Check if the appointment overlaps with this slot
            if (current_slot < appointment.end_time and slot_end > appointment.start_time):
                conflict = True
                break

        if not conflict:
            time_slots.append({
                'start_time': current_slot.time(),
                'end_time': slot_end.time(),
                'formatted_time': current_slot.strftime('%I:%M %p')
            })

        # Move to the next slot (15 minutes later)
        current_slot += timedelta(minutes=15)

    return time_slots
