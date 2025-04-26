from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q

from apps.core.models import User, BusinessSettings
from apps.appointments.models import Appointment
from .models import UserLog, EmailTemplate
from .forms_email import EmailForm, EmailTemplateForm

@login_required
def admin_email_dashboard(request):
    """
    View for the email dashboard.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all clients
    clients = User.objects.filter(role='client').order_by('-date_joined')

    # Get email templates
    templates = EmailTemplate.objects.all().order_by('-created_at')

    # Get recent emails sent
    recent_emails = UserLog.objects.filter(
        action='email_sent'
    ).order_by('-created_at')[:10]

    return render(request, 'admin_panel/email_dashboard.html', {
        'title': 'Email Dashboard',
        'clients': clients,
        'templates': templates,
        'recent_emails': recent_emails,
    })

@login_required
def admin_email_compose(request):
    """
    View for composing and sending emails to clients.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get all clients
    clients = User.objects.filter(role='client').order_by('first_name', 'last_name')

    # Get email templates
    templates = EmailTemplate.objects.all().order_by('name')

    # Get business settings for default sender
    try:
        business_settings = BusinessSettings.objects.get(id=1)
        default_sender = business_settings.email
        business_name = business_settings.business_name
    except BusinessSettings.DoesNotExist:
        default_sender = settings.DEFAULT_FROM_EMAIL
        business_name = "Barberian"

    if request.method == 'POST':
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():
            # Get form data
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipients = form.cleaned_data['recipients']
            attachments = request.FILES.getlist('attachments')

            # Send email to each recipient
            successful_sends = 0
            failed_sends = 0

            for recipient_id in recipients:
                try:
                    recipient = User.objects.get(id=recipient_id)

                    # Create HTML email
                    html_message = render_to_string('admin_panel/email_template.html', {
                        'recipient_name': recipient.get_full_name(),
                        'message': message,
                        'business_name': business_name,
                        'current_year': timezone.now().year,
                        'subject': subject,
                    })

                    # Create plain text version
                    plain_message = strip_tags(html_message)

                    # Create email
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=f"{business_name} <{default_sender}>",
                        to=[recipient.email],
                        reply_to=[default_sender],
                    )

                    # Attach HTML version
                    email.attach_alternative(html_message, "text/html")

                    # Attach files if any
                    for attachment in attachments:
                        email.attach(attachment.name, attachment.read(), attachment.content_type)

                    # Send email
                    email.send(fail_silently=False)

                    # Log the action
                    UserLog.objects.create(
                        user=request.user,
                        action='email_sent',
                        entity_type='user',
                        entity_id=recipient.id,
                        details=f"Email sent to {recipient.email} with subject: {subject}"
                    )

                    successful_sends += 1

                except User.DoesNotExist:
                    failed_sends += 1
                except Exception as e:
                    failed_sends += 1
                    print(f"Error sending email to {recipient_id}: {str(e)}")

            # Show success message
            if successful_sends > 0:
                messages.success(request, f"Email sent successfully to {successful_sends} recipient(s).")

            # Show error message if any
            if failed_sends > 0:
                messages.error(request, f"Failed to send email to {failed_sends} recipient(s).")

            return redirect('admin_panel:email_dashboard')
    else:
        form = EmailForm()

    return render(request, 'admin_panel/email_compose.html', {
        'title': 'Compose Email',
        'form': form,
        'clients': clients,
        'templates': templates,
        'default_sender': default_sender,
        'business_name': business_name,
    })

@login_required
def admin_email_template_create(request):
    """
    View for creating an email template.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()

            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='create',
                entity_type='email_template',
                entity_id=template.id,
                details=f"Created email template: {template.name}"
            )

            messages.success(request, "Email template created successfully.")
            return redirect('admin_panel:email_dashboard')
    else:
        form = EmailTemplateForm()

    return render(request, 'admin_panel/email_template_form.html', {
        'title': 'Create Email Template',
        'form': form,
    })

@login_required
def admin_email_template_edit(request, template_id):
    """
    View for editing an email template.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the template
    template = get_object_or_404(EmailTemplate, id=template_id)

    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            updated_template = form.save(commit=False)
            # Keep the original created_by
            updated_template.save()

            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='update',
                entity_type='email_template',
                entity_id=template.id,
                details=f"Updated email template: {updated_template.name}"
            )

            messages.success(request, "Email template updated successfully.")
            return redirect('admin_panel:email_dashboard')
    else:
        form = EmailTemplateForm(instance=template)

    return render(request, 'admin_panel/email_template_form.html', {
        'title': 'Edit Email Template',
        'form': form,
        'template': template,
    })

@login_required
def admin_email_template_delete(request, template_id):
    """
    View for deleting an email template.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the template
    template = get_object_or_404(EmailTemplate, id=template_id)

    if request.method == 'POST':
        # Log the action
        UserLog.objects.create(
            user=request.user,
            action='delete',
            entity_type='email_template',
            entity_id=template.id,
            details=f"Deleted email template: {template.name}"
        )

        # Delete the template
        template.delete()

        messages.success(request, "Email template deleted successfully.")
        return redirect('admin_panel:email_dashboard')

    return render(request, 'admin_panel/email_template_delete.html', {
        'title': 'Delete Email Template',
        'template': template,
    })

@login_required
def admin_email_template_get(request, template_id):
    """
    AJAX view for getting an email template.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get the template
    try:
        template = EmailTemplate.objects.get(id=template_id)
        return JsonResponse({
            'subject': template.subject,
            'message': template.message,
        })
    except EmailTemplate.DoesNotExist:
        return JsonResponse({'error': 'Template not found'}, status=404)

@login_required
def admin_email_client_list(request):
    """
    AJAX view for getting a filtered list of clients.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get query parameter
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')

    # Base query
    clients = User.objects.filter(role='client')

    # Apply filter
    if filter_type == 'recent':
        # Clients who joined in the last 30 days
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        clients = clients.filter(date_joined__gte=thirty_days_ago)
    elif filter_type == 'active':
        # Clients with at least one appointment
        clients = clients.filter(appointment__isnull=False).distinct()
    elif filter_type == 'inactive':
        # Clients with no appointments
        clients = clients.filter(appointment__isnull=True)

    # Apply search query if provided
    if query:
        clients = clients.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    # Limit to 50 results
    clients = clients[:50]

    # Format the response
    client_list = []
    for client in clients:
        client_list.append({
            'id': client.id,
            'name': client.get_full_name(),
            'email': client.email,
            'phone': client.phone_number or '',
            'joined': client.date_joined.strftime('%Y-%m-%d'),
        })

    return JsonResponse({'clients': client_list})
