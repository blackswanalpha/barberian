#!/usr/bin/env python
"""
Script to book an appointment in the Barberian system.

This script creates a test client (if needed) and books an appointment.
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
import pytz

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberian.settings')
django.setup()

from django.utils import timezone
from django.conf import settings
from apps.core.models import User
from apps.services.models import Service
from apps.appointments.models import Appointment

# Get the current timezone from Django settings
TIMEZONE = pytz.timezone(settings.TIME_ZONE)

def create_test_client():
    """
    Create a test client if it doesn't exist.
    """
    email = "test_client@example.com"
    password = "Test1234!"
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        print(f"Using existing test client: {user.get_full_name()}")
        return user
    
    # Create a new user
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="Client",
        phone_number="(555) 123-4567",
        role='client'
    )
    print(f"Created new test client: {user.get_full_name()}")
    return user

def book_appointment(client, service_id=None, staff_id=None, date_str=None, time_str=None):
    """
    Book an appointment for the client.
    
    Args:
        client: The client user object
        service_id: Optional service ID (if None, a random service will be selected)
        staff_id: Optional staff ID (if None, a random staff will be selected)
        date_str: Optional date string in format 'YYYY-MM-DD' (if None, tomorrow will be used)
        time_str: Optional time string in format 'HH:MM' (if None, 10:00 will be used)
    
    Returns:
        The created appointment object
    """
    print("\n=== Booking an appointment ===")
    
    # Get the service
    if service_id:
        service = Service.objects.get(id=service_id)
    else:
        service = random.choice(list(Service.objects.filter(is_active=True)))
    print(f"Selected service: {service.name}")
    
    # Get the staff member
    if staff_id:
        staff = User.objects.get(id=staff_id, role='staff')
    else:
        staff = random.choice(list(User.objects.filter(role='staff', is_active=True)))
    print(f"Selected staff: {staff.get_full_name()}")
    
    # Set appointment time
    if date_str:
        year, month, day = map(int, date_str.split('-'))
    else:
        now = timezone.now()
        year, month, day = now.year, now.month, now.day + 1
    
    if time_str:
        hour, minute = map(int, time_str.split(':'))
    else:
        hour, minute = 10, 0
    
    # Create a timezone-aware datetime
    start_time = timezone.make_aware(
        datetime(year, month, day, hour, minute, 0),
        TIMEZONE
    )
    end_time = start_time + timedelta(minutes=service.duration)
    
    # Create the appointment
    appointment = Appointment.objects.create(
        client=client,
        staff=staff,
        service=service,
        start_time=start_time,
        end_time=end_time,
        status='pending'
    )
    
    print(f"Booked appointment: {appointment}")
    print(f"  Service: {service.name}")
    print(f"  Staff: {staff.get_full_name()}")
    print(f"  Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Status: {appointment.status}")
    
    return appointment

def view_client_appointments(client):
    """
    View all appointments for the client.
    """
    print("\n=== Client Appointments ===")
    
    appointments = Appointment.objects.filter(client=client).order_by('start_time')
    
    if not appointments:
        print("No appointments found.")
        return []
    
    print(f"Found {len(appointments)} appointment(s):")
    for i, appointment in enumerate(appointments, 1):
        print(f"{i}. Service: {appointment.service.name}")
        print(f"   Staff: {appointment.staff.get_full_name()}")
        print(f"   Time: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Status: {appointment.status}")
        print()
    
    return appointments

def main():
    """
    Main function to run the script.
    """
    print("=== Barberian Appointment Booking ===")
    
    # Create or get test client
    client = create_test_client()
    
    # Parse command line arguments
    service_id = None
    staff_id = None
    date_str = None
    time_str = None
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--service' and i + 1 < len(args):
            service_id = int(args[i + 1])
            i += 2
        elif args[i] == '--staff' and i + 1 < len(args):
            staff_id = int(args[i + 1])
            i += 2
        elif args[i] == '--date' and i + 1 < len(args):
            date_str = args[i + 1]
            i += 2
        elif args[i] == '--time' and i + 1 < len(args):
            time_str = args[i + 1]
            i += 2
        else:
            i += 1
    
    # Book the appointment
    appointment = book_appointment(client, service_id, staff_id, date_str, time_str)
    
    # View all appointments
    view_client_appointments(client)
    
    print("\n=== Appointment Booking Completed ===")

if __name__ == "__main__":
    main()
