from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from apps.services.models import Service, Category
from apps.core.models import BusinessSettings, BusinessHours, User
from apps.clients.forms import ClientProfileForm, ClientPasswordChangeForm
from django.http import HttpResponse

def splash_screen(request):
    """
    View for the splash screen.
    """
    # Check if the user has a cookie indicating they've seen the splash screen
    if request.COOKIES.get('seen_splash'):
        # If they have, redirect to home
        return redirect('client_portal:home')

    # Otherwise, show the splash screen
    return render(request, 'splash_screen.html')

def home(request):
    """
    View for the home page of the client portal.
    """
    # Get business settings
    business_settings = BusinessSettings.objects.first()

    # Get featured services (limit to 3)
    featured_services = Service.objects.filter(is_active=True).order_by('?')[:3]

    response = render(request, 'client_portal/home.html', {
        'title': 'Welcome to Barberian',
        'business_settings': business_settings,
        'featured_services': featured_services,
    })

    # Set a cookie to indicate the user has seen the splash screen
    # This cookie will expire after 1 day (86400 seconds)
    response.set_cookie('seen_splash', 'true', max_age=86400)

    return response

def about(request):
    """
    View for the about page.
    """
    # Get business settings
    business_settings = BusinessSettings.objects.first()

    return render(request, 'client_portal/about.html', {
        'title': 'About Us',
        'business_settings': business_settings,
    })

def services_list(request):
    """
    View for the services list page.
    """
    # Get all active categories
    categories = Category.objects.filter(is_active=True)

    # Get all active services
    services = Service.objects.filter(is_active=True)

    return render(request, 'client_portal/services.html', {
        'title': 'Our Services',
        'categories': categories,
        'services': services,
    })

def service_detail(request, service_id):
    """
    View for the service detail page.
    """
    # Get the service
    service = get_object_or_404(Service, id=service_id, is_active=True)

    # Get related services (same category, excluding current service)
    related_services = Service.objects.filter(
        category=service.category,
        is_active=True
    ).exclude(id=service.id)[:3]

    return render(request, 'client_portal/service_detail.html', {
        'title': service.name,
        'service': service,
        'related_services': related_services,
    })

def contact(request):
    """
    View for the contact page.
    """
    # Get business settings
    business_settings = BusinessSettings.objects.first()

    # Get business hours
    business_hours = BusinessHours.objects.all().order_by('day_of_week')

    return render(request, 'client_portal/contact.html', {
        'title': 'Contact Us',
        'business_settings': business_settings,
        'business_hours': business_hours,
    })

def staff_list(request):
    """
    View for the staff list page.
    """
    # Get all active staff members
    staff_members = User.objects.filter(role='staff', is_active=True)

    return render(request, 'client_portal/staff_list.html', {
        'title': 'Our Staff',
        'staff_members': staff_members,
    })

def staff_detail(request, staff_id):
    """
    View for the staff detail page.
    """
    # Get the staff member
    staff_member = get_object_or_404(User, id=staff_id, role='staff', is_active=True)

    # Get the services offered by this staff member
    # Since we don't have a direct relationship between services and staff,
    # we'll just show all active services for now
    services = Service.objects.filter(is_active=True)[:5]

    return render(request, 'client_portal/staff_detail.html', {
        'title': staff_member.get_full_name(),
        'staff_member': staff_member,
        'services': services,
    })

@login_required
def profile(request):
    """
    View for the user profile page.
    """
    return render(request, 'client_portal/profile.html', {
        'title': 'My Profile',
    })

@login_required
def edit_profile(request):
    """
    View for editing user profile information.
    """
    if request.method == 'POST':
        form = ClientProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('client_portal:profile')
    else:
        form = ClientProfileForm(instance=request.user)

    return render(request, 'client_portal/edit_profile.html', {
        'title': 'Edit Profile',
        'form': form
    })

@login_required
def change_password(request):
    """
    View for changing user password.
    """
    if request.method == 'POST':
        form = ClientPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('client_portal:profile')
    else:
        form = ClientPasswordChangeForm(request.user)

    return render(request, 'client_portal/change_password.html', {
        'title': 'Change Password',
        'form': form
    })
