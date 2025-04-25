# Barberian - Barbershop Management System

Barberian is a comprehensive barbershop management system designed to streamline operations for barbershop owners, staff, and clients.

## Features

- **Admin Portal**: Manage staff, services, appointments, and business operations
- **Client Portal**: Book appointments, view services, and manage profiles
- **Staff Management**: Add, edit, and remove staff profiles, manage schedules
- **Service Management**: Create and manage service categories and services
- **Appointment Management**: Book, edit, and cancel appointments
- **Client Management**: View and manage client profiles
- **Business Settings**: Configure business hours, manage business information

## Project Structure

The project follows a monolithic Django structure with apps organized in folders:

- **core**: Shared utilities, business hours, auth, email
- **clients**: Client profiles and preferences
- **staff**: Staff profiles and schedules
- **services**: Service categories and services
- **appointments**: Appointment booking and management
- **notifications**: Email and SMS notifications
- **admin_panel**: Admin interface customizations
- **client_portal**: Public-facing views

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/blackswanalpha/barberian.git
   cd barberian
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database settings (optional, defaults to SQLite)
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=barberian
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432

   # Email settings (optional)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_email_password
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Populate the database with sample data:
   ```
   python scripts/populate_db.py
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the application at http://localhost:8000

9. Login credentials for testing:
   - Admin: admin@barberian.com / admin1234
   - Staff: john@barberian.com / staff1234
   - Client: client1@example.com / client1234

## License

This project is licensed under the MIT License - see the LICENSE file for details.
