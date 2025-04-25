#!/usr/bin/env python
"""
Test client script for Barberian.

This script creates a test client and performs various operations:
- Book an appointment
- View appointments
- Reschedule an appointment
- Cancel an appointment
- Change profile name
- Change password
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

from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from apps.core.models import User
from apps.services.models import Service
from apps.appointments.models import Appointment
from apps.clients.forms import ClientRegistrationForm
from django.contrib.auth.forms import PasswordChangeForm

# Get the current timezone from Django settings
TIMEZONE = pytz.timezone(settings.TIME_ZONE)


class TestClient:
    """
    Test client class for Barberian.
    """
    def __init__(self):
        self.user = None
        self.email = f"test_client_{int(timezone.now().timestamp())}@example.com"
        self.password = "Test1234!"
        self.first_name = "Test"
        self.last_name = "Client"
        self.phone_number = "(555) 123-4567"
        self.appointments = []

    def create_client(self):
        """
        Create a new test client.
        """
        print(f"\n=== Creating test client: {self.email} ===")

        # Check if user already exists
        if User.objects.filter(email=self.email).exists():
            self.user = User.objects.get(email=self.email)
            print(f"User already exists: {self.user.get_full_name()}")
            return self.user

        # Create user using the registration form
        form_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'password1': self.password,
            'password2': self.password,
        }

        form = ClientRegistrationForm(data=form_data)
        if form.is_valid():
            self.user = form.save()
            print(f"Created user: {self.user.get_full_name()}")
        else:
            print("Error creating user:")
            for field, errors in form.errors.items():
                print(f"  {field}: {', '.join(errors)}")

            # Try creating user directly
            self.user = User.objects.create_user(
                email=self.email,
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name,
                phone_number=self.phone_number,
                role='client'
            )
            print(f"Created user directly: {self.user.get_full_name()}")

        return self.user

    def book_appointment(self):
        """
        Book a new appointment.
        """
        print("\n=== Booking an appointment ===")

        # Get a random service
        service = random.choice(list(Service.objects.filter(is_active=True)))
        print(f"Selected service: {service.name}")

        # Get a random staff member
        staff = random.choice(list(User.objects.filter(role='staff', is_active=True)))
        print(f"Selected staff: {staff.get_full_name()}")

        # Set appointment time (next day, 10:00 AM)
        # Create a timezone-aware datetime
        now = timezone.now()
        start_time = timezone.make_aware(
            datetime(now.year, now.month, now.day, 10, 0, 0) + timedelta(days=1),
            TIMEZONE
        )
        end_time = start_time + timedelta(minutes=service.duration)

        # Create the appointment
        appointment = Appointment.objects.create(
            client=self.user,
            staff=staff,
            service=service,
            start_time=start_time,
            end_time=end_time,
            status='pending'
        )

        self.appointments.append(appointment)
        print(f"Booked appointment: {appointment}")
        print(f"  Service: {service.name}")
        print(f"  Staff: {staff.get_full_name()}")
        print(f"  Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Status: {appointment.status}")

        return appointment

    def view_appointments(self):
        """
        View all appointments for the client.
        """
        print("\n=== Viewing appointments ===")

        appointments = Appointment.objects.filter(client=self.user).order_by('start_time')
        self.appointments = list(appointments)

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

    def reschedule_appointment(self, appointment=None):
        """
        Reschedule an existing appointment.
        """
        print("\n=== Rescheduling an appointment ===")

        # Get the appointment to reschedule
        if appointment is None:
            appointments = self.view_appointments()
            if not appointments:
                print("No appointments to reschedule.")
                return None

            # Get the first pending or confirmed appointment
            for appt in appointments:
                if appt.status in ['pending', 'confirmed']:
                    appointment = appt
                    break

            if appointment is None:
                print("No pending or confirmed appointments to reschedule.")
                return None

        print(f"Rescheduling appointment: {appointment}")
        print(f"  Current time: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}")

        # Set new appointment time (add 1 day)
        # Create new timezone-aware datetime objects
        start_dt = appointment.start_time
        new_start_time = timezone.make_aware(
            datetime(start_dt.year, start_dt.month, start_dt.day, start_dt.hour, start_dt.minute) + timedelta(days=1),
            TIMEZONE
        )

        end_dt = appointment.end_time
        new_end_time = timezone.make_aware(
            datetime(end_dt.year, end_dt.month, end_dt.day, end_dt.hour, end_dt.minute) + timedelta(days=1),
            TIMEZONE
        )

        # Update the appointment
        appointment.start_time = new_start_time
        appointment.end_time = new_end_time
        appointment.save()

        print(f"Appointment rescheduled to: {new_start_time.strftime('%Y-%m-%d %H:%M')}")
        return appointment

    def cancel_appointment(self, appointment=None):
        """
        Cancel an existing appointment.
        """
        print("\n=== Cancelling an appointment ===")

        # Get the appointment to cancel
        if appointment is None:
            appointments = self.view_appointments()
            if not appointments:
                print("No appointments to cancel.")
                return None

            # Get the first pending or confirmed appointment
            for appt in appointments:
                if appt.status in ['pending', 'confirmed']:
                    appointment = appt
                    break

            if appointment is None:
                print("No pending or confirmed appointments to cancel.")
                return None

        print(f"Cancelling appointment: {appointment}")
        print(f"  Service: {appointment.service.name}")
        print(f"  Staff: {appointment.staff.get_full_name()}")
        print(f"  Time: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}")

        # Cancel the appointment
        appointment.status = 'cancelled'
        appointment.save()

        print("Appointment cancelled successfully.")
        return appointment

    def change_profile_name(self, new_first_name=None, new_last_name=None):
        """
        Change the client's profile name.
        """
        print("\n=== Changing profile name ===")

        if new_first_name is None:
            new_first_name = f"Updated{self.first_name}"

        if new_last_name is None:
            new_last_name = f"Updated{self.last_name}"

        print(f"Current name: {self.user.get_full_name()}")
        print(f"New name: {new_first_name} {new_last_name}")

        # Update the user's name
        self.user.first_name = new_first_name
        self.user.last_name = new_last_name
        self.user.save()

        print(f"Profile name updated to: {self.user.get_full_name()}")
        return self.user

    def change_password(self, new_password=None):
        """
        Change the client's password.
        """
        print("\n=== Changing password ===")

        if new_password is None:
            new_password = f"{self.password}Updated"

        print(f"Current password: {self.password}")
        print(f"New password: {new_password}")

        # Change the password
        self.user.set_password(new_password)
        self.user.save()

        # Update the stored password
        old_password = self.password
        self.password = new_password

        # Verify the password change
        user = authenticate(email=self.email, password=new_password)
        if user is not None:
            print("Password changed successfully and verified.")
        else:
            print("Password change failed verification.")
            # Revert to old password if verification failed
            self.user.set_password(old_password)
            self.user.save()
            self.password = old_password

        return self.user


def run_test():
    """
    Run the test client operations.
    """
    print("=== Starting Barberian Test Client ===")

    # Create test client
    client = TestClient()
    client.create_client()

    # Book an appointment
    appointment = client.book_appointment()

    # View appointments
    client.view_appointments()

    print("\n=== Test Client Operations Completed ===")


if __name__ == "__main__":
    run_test()
