from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_email_notification(subject, template_name, context, recipient_list):
    """
    Send an email notification using a template.

    Args:
        subject (str): The email subject
        template_name (str): The name of the template to use (without extension)
        context (dict): The context to render the template with
        recipient_list (list): A list of email addresses to send the email to

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        # Render the HTML content
        html_content = render_to_string(f'emails/{template_name}.html', context)

        # Create a plain text version of the HTML content
        text_content = strip_tags(html_content)

        # Create the email message
        from_email = settings.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")

        # Send the email
        msg.send()

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_appointment_confirmation(appointment):
    """
    Send an appointment confirmation email to the client.

    Args:
        appointment: The appointment object

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"Appointment Confirmation - {appointment.service.name} on {appointment.start_time.strftime('%B %d, %Y')}"
    template_name = 'appointment_confirmation'
    context = {
        'appointment': appointment,
        'client': appointment.client,
        'staff': appointment.staff,
        'service': appointment.service,
    }
    recipient_list = [appointment.client.email]

    return send_email_notification(subject, template_name, context, recipient_list)

def send_appointment_reminder(appointment):
    """
    Send an appointment reminder email to the client.

    Args:
        appointment: The appointment object

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"Appointment Reminder - {appointment.service.name} on {appointment.start_time.strftime('%B %d, %Y')}"
    template_name = 'appointment_reminder'
    context = {
        'appointment': appointment,
        'client': appointment.client,
        'staff': appointment.staff,
        'service': appointment.service,
    }
    recipient_list = [appointment.client.email]

    return send_email_notification(subject, template_name, context, recipient_list)

def send_appointment_cancellation(appointment):
    """
    Send an appointment cancellation email to the client.

    Args:
        appointment: The appointment object

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"Appointment Cancellation - {appointment.service.name} on {appointment.start_time.strftime('%B %d, %Y')}"
    template_name = 'appointment_cancellation'
    context = {
        'appointment': appointment,
        'client': appointment.client,
        'staff': appointment.staff,
        'service': appointment.service,
    }
    recipient_list = [appointment.client.email]

    return send_email_notification(subject, template_name, context, recipient_list)

def send_appointment_rescheduled(appointment, old_start_time):
    """
    Send an appointment rescheduled email to the client.

    Args:
        appointment: The appointment object
        old_start_time: The old start time of the appointment

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"Appointment Rescheduled - {appointment.service.name} on {appointment.start_time.strftime('%B %d, %Y')}"
    template_name = 'appointment_rescheduled'
    context = {
        'appointment': appointment,
        'client': appointment.client,
        'staff': appointment.staff,
        'service': appointment.service,
        'old_start_time': old_start_time,
    }
    recipient_list = [appointment.client.email]

    return send_email_notification(subject, template_name, context, recipient_list)

def send_staff_new_appointment(appointment):
    """
    Send a new appointment notification email to the staff member.

    Args:
        appointment: The appointment object

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"New Appointment - {appointment.service.name} on {appointment.start_time.strftime('%B %d, %Y')}"
    template_name = 'staff_new_appointment'
    context = {
        'appointment': appointment,
        'client': appointment.client,
        'staff': appointment.staff,
        'service': appointment.service,
    }
    recipient_list = [appointment.staff.email]

    return send_email_notification(subject, template_name, context, recipient_list)

def send_staff_appointment_cancelled(appointment):
    """
    Send an appointment cancellation notification email to the staff member.

    Args:
        appointment: The appointment object

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"Appointment Cancelled - {appointment.service.name} on {appointment.start_time.strftime('%B %d, %Y')}"
    template_name = 'staff_appointment_cancelled'
    context = {
        'appointment': appointment,
        'client': appointment.client,
        'staff': appointment.staff,
        'service': appointment.service,
    }
    recipient_list = [appointment.staff.email]

    return send_email_notification(subject, template_name, context, recipient_list)

def send_welcome_email(user):
    """
    Send a welcome email to a new user.

    Args:
        user: The user object

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"Welcome to Barberian!"
    template_name = 'welcome'
    context = {
        'user': user,
    }
    recipient_list = [user.email]

    return send_email_notification(subject, template_name, context, recipient_list)

def send_password_reset(user, reset_url):
    """
    Send a password reset email to a user.

    Args:
        user: The user object
        reset_url: The URL to reset the password

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"Password Reset Request"
    template_name = 'password_reset'
    context = {
        'user': user,
        'reset_url': reset_url,
    }
    recipient_list = [user.email]

    return send_email_notification(subject, template_name, context, recipient_list)

def send_admin_appointment_request(admin, appointment):
    """
    Send an appointment request notification to an admin.

    Args:
        admin: The admin user object
        appointment: The appointment object

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"New Appointment Request - {appointment.service.name} on {appointment.start_time.strftime('%B %d, %Y')}"
    template_name = 'admin_appointment_request'
    context = {
        'admin': admin,
        'appointment': appointment,
        'client': appointment.client,
        'service': appointment.service,
    }
    recipient_list = [admin.email]

    return send_email_notification(subject, template_name, context, recipient_list)

def send_appointment_update(appointment, changes):
    """
    Send an appointment update notification to the client.

    Args:
        appointment: The appointment object
        changes: A dictionary of changes made to the appointment

    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = f"Appointment Update - {appointment.service.name} on {appointment.start_time.strftime('%B %d, %Y')}"
    template_name = 'appointment_update'
    context = {
        'appointment': appointment,
        'client': appointment.client,
        'staff': appointment.staff,
        'service': appointment.service,
        'changes': changes,
    }
    recipient_list = [appointment.client.email]

    return send_email_notification(subject, template_name, context, recipient_list)
