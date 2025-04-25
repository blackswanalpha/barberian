#!/usr/bin/env python
"""
Script to view appointments in the Barberian system.

This script shows all appointments for a client or staff member.
"""

import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberian.settings')
django.setup()

from django.utils import timezone
from apps.core.models import User
from apps.appointments.models import Appointment

def view_appointments(user_email=None, role=None, status=None, upcoming_only=False, past_only=False):
    """
    View appointments for a user.
    
    Args:
        user_email: Email of the user to view appointments for (if None, uses test_client@example.com)
        role: Role of the user ('client' or 'staff')
        status: Filter by appointment status (e.g., 'pending', 'confirmed', 'cancelled')
        upcoming_only: Show only upcoming appointments
        past_only: Show only past appointments
    """
    print("\n=== Viewing Appointments ===")
    
    # Get the user
    if not user_email:
        user_email = "test_client@example.com"
        
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        print(f"User with email {user_email} not found.")
        return []
    
    print(f"User: {user.get_full_name()} ({user.role})")
    
    # Get appointments based on user role
    if role:
        user_role = role
    else:
        user_role = user.role
        
    if user_role == 'client':
        appointments = Appointment.objects.filter(client=user)
    elif user_role == 'staff':
        appointments = Appointment.objects.filter(staff=user)
    else:  # Admin
        appointments = Appointment.objects.all()
    
    # Filter by status if provided
    if status:
        appointments = appointments.filter(status=status)
    
    # Filter by time if requested
    now = timezone.now()
    if upcoming_only:
        appointments = appointments.filter(start_time__gt=now)
    elif past_only:
        appointments = appointments.filter(start_time__lt=now)
    
    # Order by start time
    appointments = appointments.order_by('start_time')
    
    if not appointments:
        print("No appointments found.")
        return []
    
    print(f"Found {len(appointments)} appointment(s):")
    for i, appointment in enumerate(appointments, 1):
        print(f"{i}. Service: {appointment.service.name}")
        print(f"   Client: {appointment.client.get_full_name()}")
        print(f"   Staff: {appointment.staff.get_full_name()}")
        print(f"   Time: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Status: {appointment.status}")
        print()
    
    return appointments

def main():
    """
    Main function to run the script.
    """
    print("=== Barberian Appointment Viewer ===")
    
    # Parse command line arguments
    user_email = None
    role = None
    status = None
    upcoming_only = False
    past_only = False
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--email' and i + 1 < len(args):
            user_email = args[i + 1]
            i += 2
        elif args[i] == '--role' and i + 1 < len(args):
            role = args[i + 1]
            i += 2
        elif args[i] == '--status' and i + 1 < len(args):
            status = args[i + 1]
            i += 2
        elif args[i] == '--upcoming':
            upcoming_only = True
            i += 1
        elif args[i] == '--past':
            past_only = True
            i += 1
        else:
            i += 1
    
    # View appointments
    view_appointments(user_email, role, status, upcoming_only, past_only)
    
    print("\n=== Appointment Viewing Completed ===")

if __name__ == "__main__":
    main()
