import os
import sys
import django
import random
from datetime import datetime, timedelta

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberian.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.core.models import BusinessHours, BusinessSettings
from apps.services.models import Category, Service
from apps.staff.models import Schedule

User = get_user_model()

def create_business_settings():
    """Create business settings"""
    if not BusinessSettings.objects.exists():
        print("Creating business settings...")
        BusinessSettings.objects.create(
            business_name="Barberian",
            address="123 Barber Street\nHaircut City, HC 12345",
            phone="(123) 456-7890",
            email="info@barberian.com",
            about="""
            Barberian was founded in 2010 with a simple mission: to provide exceptional grooming services in a comfortable, stylish environment.

            Our team of skilled barbers combines traditional techniques with modern styles to create looks that are both timeless and contemporary.

            We pride ourselves on attention to detail, personalized service, and creating a welcoming atmosphere for all our clients.
            """,
            facebook_url="https://facebook.com/barberian",
            instagram_url="https://instagram.com/barberian",
            twitter_url="https://twitter.com/barberian"
        )
    else:
        print("Business settings already exist.")

def create_business_hours():
    """Create business hours"""
    if not BusinessHours.objects.exists():
        print("Creating business hours...")
        # Monday to Friday: 9 AM to 7 PM
        for day in range(0, 5):
            BusinessHours.objects.create(
                day_of_week=day,
                is_open=True,
                opening_time="09:00",
                closing_time="19:00"
            )

        # Saturday: 10 AM to 6 PM
        BusinessHours.objects.create(
            day_of_week=5,
            is_open=True,
            opening_time="10:00",
            closing_time="18:00"
        )

        # Sunday: Closed
        BusinessHours.objects.create(
            day_of_week=6,
            is_open=False,
            opening_time="09:00",
            closing_time="18:00"
        )
    else:
        print("Business hours already exist.")

def create_users():
    """Create admin, staff, and client users"""
    # Check if admin exists
    if not User.objects.filter(email="admin@barberian.com").exists():
        print("Creating admin user...")
        User.objects.create_superuser(
            email="admin@barberian.com",
            password="admin1234",
            first_name="Admin",
            last_name="User",
            role="admin"
        )

    # Create staff users
    staff_data = [
        {
            "email": "john@barberian.com",
            "password": "staff1234",
            "first_name": "John",
            "last_name": "Smith",
            "phone_number": "(123) 456-7891",
            "bio": "John is a master barber with over 10 years of experience specializing in classic cuts and hot towel shaves.",
            "specialization": "Classic Cuts, Hot Towel Shaves"
        },
        {
            "email": "michael@barberian.com",
            "password": "staff1234",
            "first_name": "Michael",
            "last_name": "Johnson",
            "phone_number": "(123) 456-7892",
            "bio": "Michael is known for his modern styling techniques and attention to detail.",
            "specialization": "Modern Styles, Fades"
        },
        {
            "email": "sarah@barberian.com",
            "password": "staff1234",
            "first_name": "Sarah",
            "last_name": "Williams",
            "phone_number": "(123) 456-7893",
            "bio": "Sarah specializes in creative cuts and color services, bringing a unique perspective to men's grooming.",
            "specialization": "Creative Cuts, Color Services"
        }
    ]

    for staff in staff_data:
        if not User.objects.filter(email=staff["email"]).exists():
            print(f"Creating staff user: {staff['first_name']} {staff['last_name']}...")
            User.objects.create_user(
                email=staff["email"],
                password=staff["password"],
                first_name=staff["first_name"],
                last_name=staff["last_name"],
                phone_number=staff["phone_number"],
                bio=staff["bio"],
                specialization=staff["specialization"],
                role="staff",
                is_active=True
            )

    # Create client users
    client_data = [
        {
            "email": "client1@example.com",
            "password": "client1234",
            "first_name": "David",
            "last_name": "Brown",
            "phone_number": "(123) 456-7894"
        },
        {
            "email": "client2@example.com",
            "password": "client1234",
            "first_name": "Emily",
            "last_name": "Davis",
            "phone_number": "(123) 456-7895"
        },
        {
            "email": "client3@example.com",
            "password": "client1234",
            "first_name": "Robert",
            "last_name": "Wilson",
            "phone_number": "(123) 456-7896"
        }
    ]

    for client in client_data:
        if not User.objects.filter(email=client["email"]).exists():
            print(f"Creating client user: {client['first_name']} {client['last_name']}...")
            User.objects.create_user(
                email=client["email"],
                password=client["password"],
                first_name=client["first_name"],
                last_name=client["last_name"],
                phone_number=client["phone_number"],
                role="client",
                is_active=True
            )

def create_staff_schedules():
    """Create schedules for staff members"""
    staff_users = User.objects.filter(role="staff")

    if staff_users.exists() and not Schedule.objects.exists():
        print("Creating staff schedules...")
        for staff in staff_users:
            # Monday to Friday: 9 AM to 7 PM
            for day in range(0, 5):
                Schedule.objects.create(
                    staff=staff,
                    day_of_week=day,
                    start_time="09:00",
                    end_time="19:00",
                    is_working=True
                )

            # Saturday: 10 AM to 6 PM (only for some staff)
            if random.choice([True, False]):
                Schedule.objects.create(
                    staff=staff,
                    day_of_week=5,
                    start_time="10:00",
                    end_time="18:00",
                    is_working=True
                )
            else:
                Schedule.objects.create(
                    staff=staff,
                    day_of_week=5,
                    start_time="10:00",
                    end_time="18:00",
                    is_working=False
                )

            # Sunday: Closed for all staff
            Schedule.objects.create(
                staff=staff,
                day_of_week=6,
                start_time="09:00",
                end_time="18:00",
                is_working=False
            )
    else:
        print("Staff schedules already exist or no staff users found.")

def create_service_categories():
    """Create service categories"""
    if not Category.objects.exists():
        print("Creating service categories...")
        categories = [
            {
                "name": "Haircuts",
                "description": "Professional haircuts tailored to your style and preferences."
            },
            {
                "name": "Shaves",
                "description": "Traditional and modern shaving services for a clean, smooth look."
            },
            {
                "name": "Beard Grooming",
                "description": "Expert beard trimming, shaping, and maintenance services."
            },
            {
                "name": "Hair Treatments",
                "description": "Specialized treatments to improve the health and appearance of your hair."
            }
        ]

        for category in categories:
            Category.objects.create(
                name=category["name"],
                description=category["description"],
                is_active=True
            )
    else:
        print("Service categories already exist.")

def create_services():
    """Create services for each category"""
    categories = Category.objects.all()

    if categories.exists() and not Service.objects.exists():
        print("Creating services...")

        # Haircuts
        haircuts_category = Category.objects.get(name="Haircuts")
        haircut_services = [
            {
                "name": "Classic Haircut",
                "description": "A timeless haircut that includes a consultation, shampoo, cut, and style.",
                "price": 25.00,
                "duration": 30
            },
            {
                "name": "Premium Haircut",
                "description": "Our premium haircut service includes a detailed consultation, shampoo, precision cut, and styling with premium products.",
                "price": 35.00,
                "duration": 45
            },
            {
                "name": "Buzz Cut",
                "description": "A short, uniform cut using clippers for a low-maintenance style.",
                "price": 20.00,
                "duration": 20
            },
            {
                "name": "Kids Haircut",
                "description": "Haircut service for children under 12 years old.",
                "price": 18.00,
                "duration": 25
            }
        ]

        for service in haircut_services:
            Service.objects.create(
                name=service["name"],
                description=service["description"],
                price=service["price"],
                duration=service["duration"],
                category=haircuts_category,
                is_active=True
            )

        # Shaves
        shaves_category = Category.objects.get(name="Shaves")
        shave_services = [
            {
                "name": "Traditional Straight Razor Shave",
                "description": "Experience the luxury of a traditional hot towel straight razor shave with premium products.",
                "price": 30.00,
                "duration": 40
            },
            {
                "name": "Express Shave",
                "description": "A quick but thorough shave for when you're short on time.",
                "price": 20.00,
                "duration": 25
            },
            {
                "name": "Head Shave",
                "description": "A complete head shave with hot towel treatment and moisturizing finish.",
                "price": 35.00,
                "duration": 45
            }
        ]

        for service in shave_services:
            Service.objects.create(
                name=service["name"],
                description=service["description"],
                price=service["price"],
                duration=service["duration"],
                category=shaves_category,
                is_active=True
            )

        # Beard Grooming
        beard_category = Category.objects.get(name="Beard Grooming")
        beard_services = [
            {
                "name": "Beard Trim",
                "description": "A precise trim to shape and maintain your beard.",
                "price": 15.00,
                "duration": 20
            },
            {
                "name": "Beard Styling",
                "description": "Complete beard service including trim, shape, wash, and styling with premium products.",
                "price": 25.00,
                "duration": 30
            },
            {
                "name": "Beard Color",
                "description": "Professional beard coloring to cover gray or change your look.",
                "price": 40.00,
                "duration": 60
            }
        ]

        for service in beard_services:
            Service.objects.create(
                name=service["name"],
                description=service["description"],
                price=service["price"],
                duration=service["duration"],
                category=beard_category,
                is_active=True
            )

        # Hair Treatments
        treatment_category = Category.objects.get(name="Hair Treatments")
        treatment_services = [
            {
                "name": "Scalp Treatment",
                "description": "Therapeutic treatment to improve scalp health and address issues like dryness or dandruff.",
                "price": 35.00,
                "duration": 40
            },
            {
                "name": "Hair Mask",
                "description": "Deep conditioning treatment to restore moisture and shine to your hair.",
                "price": 30.00,
                "duration": 35
            },
            {
                "name": "Gray Blending",
                "description": "Subtle color service to reduce the appearance of gray hair for a natural look.",
                "price": 45.00,
                "duration": 60
            }
        ]

        for service in treatment_services:
            Service.objects.create(
                name=service["name"],
                description=service["description"],
                price=service["price"],
                duration=service["duration"],
                category=treatment_category,
                is_active=True
            )
    else:
        print("Services already exist or no categories found.")

if __name__ == "__main__":
    print("Starting database population script...")
    create_business_settings()
    create_business_hours()
    create_users()
    create_staff_schedules()
    create_service_categories()
    create_services()
    print("Database population completed!")
