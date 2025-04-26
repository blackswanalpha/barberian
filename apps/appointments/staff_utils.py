from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count

from apps.core.models import User
from apps.staff.models import Schedule
from apps.clients.models import PreferredStaff
from .models import Appointment

def find_available_staff(service, date, time_str=None):
    """
    Find available staff members for a given service, date, and optionally time.

    Args:
        service: The service object
        date: The date object
        time_str: Optional time string in format 'HH:MM'

    Returns:
        A list of available staff members
    """
    # Get all active staff members who can provide this service
    staff_members = User.objects.filter(role='staff', is_active=True)

    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = date.weekday()

    # Filter staff members who are working on this day
    available_staff = []

    for staff in staff_members:
        try:
            # Check if the staff member is working on this day
            schedule = Schedule.objects.get(staff=staff, day_of_week=day_of_week, is_working=True)

            # If a specific time is provided, check if the staff member is available at that time
            if time_str:
                # Parse the time string
                hour, minute = map(int, time_str.split(':'))
                time_obj = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()

                # Create timezone-aware datetime objects for the appointment start and end
                start_datetime = timezone.make_aware(datetime.combine(date, time_obj))
                end_datetime = start_datetime + timedelta(minutes=service.duration)

                # Check if the appointment is within the staff's working hours
                staff_start = timezone.make_aware(datetime.combine(date, schedule.start_time))
                staff_end = timezone.make_aware(datetime.combine(date, schedule.end_time))

                if start_datetime < staff_start or end_datetime > staff_end:
                    continue

                # Check if the staff member has any overlapping appointments
                overlapping_appointments = Appointment.objects.filter(
                    staff=staff,
                    start_time__lt=end_datetime,
                    end_time__gt=start_datetime,
                    status__in=['pending', 'confirmed']
                )

                if overlapping_appointments.exists():
                    continue

            # If we get here, the staff member is available
            available_staff.append(staff)

        except Schedule.DoesNotExist:
            # Staff member is not working on this day
            continue

    return available_staff

def select_best_staff(client, service, date, time_str=None):
    """
    Select the best available staff member for a given client, service, date, and time.

    Args:
        client: The client user object
        service: The service object
        date: The date object
        time_str: Optional time string in format 'HH:MM'

    Returns:
        The selected staff member or None if no staff is available
    """
    # Find available staff members
    available_staff = find_available_staff(service, date, time_str)

    if not available_staff:
        return None

    # Check if the client has preferred staff members
    preferred_staff_ids = PreferredStaff.objects.filter(
        client=client
    ).values_list('staff_id', flat=True)

    # First, try to assign a preferred staff member if available
    for staff in available_staff:
        if staff.id in preferred_staff_ids:
            return staff

    # If no preferred staff is available, select the staff member with the least appointments for the day
    if time_str:
        # If a specific time is provided, we've already filtered for availability
        # Just select the staff member with the least appointments for the day
        staff_with_counts = []

        for staff in available_staff:
            # Count appointments for this staff member on this date
            # Use timezone-aware date filtering
            appointment_count = Appointment.objects.filter(
                staff=staff,
                start_time__date=date,
                status__in=['pending', 'confirmed']
            ).count()

            staff_with_counts.append((staff, appointment_count))

        # Sort by appointment count (ascending)
        staff_with_counts.sort(key=lambda x: x[1])

        # Return the staff member with the least appointments
        if staff_with_counts:
            return staff_with_counts[0][0]

    # If we get here and still have available staff, just return the first one
    return available_staff[0] if available_staff else None

def get_available_time_slots(service, date):
    """
    Get all available time slots for a given service and date across all staff members.

    Args:
        service: The service object
        date: The date object

    Returns:
        A list of available time slots as time objects
    """
    # Get all active staff members
    staff_members = User.objects.filter(role='staff', is_active=True)
    print(f"Found {staff_members.count()} active staff members")

    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = date.weekday()
    print(f"Day of week: {day_of_week} (0=Monday, 6=Sunday)")

    # Get all available time slots
    all_time_slots = set()

    for staff in staff_members:
        print(f"Checking staff member: {staff.get_full_name()} (ID: {staff.id})")
        try:
            # Check if the staff member is working on this day
            schedule = Schedule.objects.get(staff=staff, day_of_week=day_of_week, is_working=True)
            print(f"  Staff is working this day. Hours: {schedule.start_time} - {schedule.end_time}")

            # Generate time slots based on the schedule and service duration
            slots = _generate_time_slots(schedule.start_time, schedule.end_time, service.duration)
            print(f"  Generated {len(slots)} time slots")

            # Filter out time slots that are already booked
            available_slots = _filter_available_slots(staff, date, slots, service.duration)
            print(f"  After filtering, {len(available_slots)} slots are available")

            # Add available slots to the set
            all_time_slots.update(available_slots)

        except Schedule.DoesNotExist:
            # Staff member is not working on this day
            print(f"  Staff is not working this day")
            continue

    # Convert the set to a sorted list
    result = sorted(list(all_time_slots))
    print(f"Total available time slots across all staff: {len(result)}")
    if len(result) == 0:
        print("WARNING: No available time slots found!")
    else:
        print(f"Available times: {[slot.strftime('%H:%M') for slot in result[:5]]}...")

    return result

def _generate_time_slots(start_time, end_time, duration):
    """
    Generate time slots based on the schedule and service duration.
    """
    slots = []

    # Use a fixed date for time calculations to avoid timezone issues
    current_date = datetime.now().date()

    # Create datetime objects for start and end times
    current_time = datetime.combine(current_date, start_time)
    end_datetime = datetime.combine(current_date, end_time)

    # Subtract service duration to ensure the appointment ends before the schedule end time
    end_datetime = end_datetime - timedelta(minutes=duration)

    print(f"  Generating slots from {current_time.time()} to {end_datetime.time()} with duration {duration} minutes")

    # Generate slots at 15-minute intervals
    while current_time <= end_datetime:
        # Only add future time slots if the date is today
        if current_date == timezone.localtime().date():
            # Skip time slots that are in the past
            if current_time.time() > timezone.localtime().time():
                slots.append(current_time.time())
        else:
            # For future dates, add all time slots
            slots.append(current_time.time())

        current_time += timedelta(minutes=15)

    print(f"  Generated {len(slots)} slots")
    return slots

def _filter_available_slots(staff, date, time_slots, duration):
    """
    Filter out time slots that are already booked.
    """
    available_slots = []

    for slot in time_slots:
        # Convert the time slot to a timezone-aware datetime
        start_datetime = timezone.make_aware(datetime.combine(date, slot))
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
