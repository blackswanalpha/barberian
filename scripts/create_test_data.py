import os
import django
import random
from datetime import datetime, timedelta, time
import urllib.request
from django.utils import timezone
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberian.settings')
django.setup()

# Import models
from apps.core.models import User
from apps.services.models import Service, Category, ServiceMedia
from apps.appointments.models import Appointment
from apps.staff.models import Schedule, StaffSettings
from apps.reviews.models import Review

def create_test_media():
    """Create test media for services"""
    print("Creating test media...")

    # Image URLs for different service types
    haircut_images = [
        'https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1622286342621-4bd786c2447c?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1621605815971-fbc98d665033?w=800&auto=format&fit=crop',
    ]

    beard_images = [
        'https://images.unsplash.com/photo-1621605815971-fbc98d665033?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1517832606299-7ae9b720a186?w=800&auto=format&fit=crop',
    ]

    facial_images = [
        'https://images.unsplash.com/photo-1560750588-73207b1ef5b8?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1598524374912-6b0b0bdd00f9?w=800&auto=format&fit=crop',
    ]

    # Get all services
    services = Service.objects.all()

    for service in services:
        # Choose appropriate images based on service name
        if 'haircut' in service.name.lower() or 'cut' in service.name.lower():
            image_urls = haircut_images
        elif 'beard' in service.name.lower() or 'shave' in service.name.lower():
            image_urls = beard_images
        else:
            image_urls = facial_images

        # Create 1-3 images for each service
        num_images = random.randint(1, 3)
        for i in range(num_images):
            try:
                # Download image
                img_temp = NamedTemporaryFile(delete=True)
                img_url = random.choice(image_urls)
                urllib.request.urlretrieve(img_url, img_temp.name)

                # Create media object
                media = ServiceMedia()
                media.service = service
                media.media_type = 'image'
                media.is_primary = (i == 0)  # First image is primary

                # Save image to media object
                file_name = f"{service.name.replace(' ', '_').lower()}_{i+1}.jpg"
                media.file.save(file_name, File(img_temp))
                media.save()

                print(f"Created media for {service.name}: {file_name}")
            except Exception as e:
                print(f"Error creating media for {service.name}: {str(e)}")

def create_staff_schedules():
    """Create test schedules for staff members"""
    print("Creating staff schedules...")

    # Get all staff members
    staff_members = User.objects.filter(role='staff')

    for staff in staff_members:
        # Create staff settings if not exists
        staff_settings, created = StaffSettings.objects.get_or_create(staff=staff)

        # Create schedules for each day of the week
        for day in range(7):
            # Random availability (80% chance of being available)
            is_working = random.random() < 0.8

            if is_working:
                # Random start time between 8 AM and 10 AM
                start_hour = random.randint(8, 10)
                start_time = time(start_hour, 0)

                # Random end time between 5 PM and 8 PM
                end_hour = random.randint(17, 20)
                end_time = time(end_hour, 0)
            else:
                # Not available, but set default times
                start_time = time(9, 0)
                end_time = time(17, 0)

            # Create or update schedule
            schedule, created = Schedule.objects.update_or_create(
                staff=staff,
                day_of_week=day,
                defaults={
                    'is_working': is_working,
                    'start_time': start_time,
                    'end_time': end_time
                }
            )

            if created:
                print(f"Created schedule for {staff.get_full_name()} on day {day}")
            else:
                print(f"Updated schedule for {staff.get_full_name()} on day {day}")

        print(f"Created schedules for {staff.get_full_name()}")

def create_reviews():
    """Create test reviews for staff members"""
    print("Creating reviews...")

    # Get all appointments
    appointments = Appointment.objects.filter(status__in=['completed', 'confirmed'])

    for appointment in appointments:
        # 70% chance of having a review
        if random.random() < 0.7:
            # Random rating 3-5
            rating = random.randint(3, 5)

            # Random comment
            comments = [
                "Great service, very professional!",
                "I'm very happy with my haircut.",
                "The staff was friendly and attentive.",
                "Will definitely come back again.",
                "Excellent experience overall.",
                "Very skilled barber, I'm impressed.",
                "The place is clean and welcoming.",
                "Best haircut I've had in a while.",
                "Highly recommended!",
                "Good service but a bit pricey."
            ]
            comment = random.choice(comments)

            # Create review
            review, created = Review.objects.get_or_create(
                appointment=appointment,
                defaults={
                    'client': appointment.client,
                    'staff': appointment.staff,
                    'rating': rating,
                    'comment': comment,
                    'created_at': appointment.start_time + timedelta(days=1)
                }
            )

            if created:
                print(f"Created review for {appointment.staff.get_full_name()} by {appointment.client.get_full_name()}: {rating}/5")

if __name__ == '__main__':
    create_test_media()
    create_reviews()

    print("Test data creation completed!")
