#!/usr/bin/env python
"""
Script to cancel an appointment in the Barberian system.
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
        print(f"{i}. ID: {appointment.id}")
        print(f"   Service: {appointment.service.name}")
        print(f"   Staff: {appointment.staff.get_full_name()}")
        print(f"   Time: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Status: {appointment.status}")
        print()
    
    return appointments

def cancel_appointment(appointment_id):
    """
    Cancel an appointment.
    
    Args:
        appointment_id: ID of the appointment to cancel
    """
    print(f"\n=== Cancelling Appointment ID: {appointment_id} ===")
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        print(f"Appointment with ID {appointment_id} not found.")
        return None
    
    # Check if the appointment can be cancelled
    if appointment.status not in ['pending', 'confirmed']:
        print(f"Cannot cancel appointment with status '{appointment.status}'.")
        return None
    
    # Check if the appointment is in the past
    if appointment.start_time < timezone.now():
        print("Cannot cancel a past appointment.")
        return None
    
    print(f"Appointment details:")
    print(f"  Service: {appointment.service.name}")
    print(f"  Client: {appointment.client.get_full_name()}")
    print(f"  Staff: {appointment.staff.get_full_name()}")
    print(f"  Time: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Status: {appointment.status}")
    
    # Cancel the appointment
    appointment.status = 'cancelled'
    appointment.save()
    
    print("Appointment cancelled successfully.")
    return appointment

def main():
    """
    Main function to run the script.
    """
    print("=== Barberian Appointment Cancellation ===")
    
    # Parse command line arguments
    appointment_id = None
    user_email = None
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--id' and i + 1 < len(args):
            appointment_id = int(args[i + 1])
            i += 2
        elif args[i] == '--email' and i + 1 < len(args):
            user_email = args[i + 1]
            i += 2
        else:
            i += 1
    
    # If no appointment ID is provided, show the user's appointments
    if not appointment_id:
        if not user_email:
            user_email = "test_client@example.com"
        
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            print(f"User with email {user_email} not found.")
            return
        
        appointments = view_client_appointments(user)
        
        if not appointments:
            return
        
        # Ask for the appointment ID to cancel
        try:
            appointment_id = int(input("\nEnter the ID of the appointment to cancel: "))
        except ValueError:
            print("Invalid input. Please enter a valid appointment ID.")
            return
    
    # Cancel the appointment
    cancel_appointment(appointment_id)
    
    print("\n=== Appointment Cancellation Completed ===")

if __name__ == "__main__":
    main()
