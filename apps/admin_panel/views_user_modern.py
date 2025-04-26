from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from apps.core.models import User
from apps.services.models import Service
from apps.staff.models import StaffSettings
from .models import UserLog
from .forms import UserForm, UserEditForm, StaffForm

@login_required
def admin_user_create_modern(request):
    """
    Modern view for creating a new user.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # If role is staff, handle staff-specific fields
            if user.role == 'staff':
                # Create staff settings
                staff_settings, created = StaffSettings.objects.get_or_create(staff=user)
                
                # Handle bio
                bio = request.POST.get('bio', '')
                if bio:
                    user.bio = bio
                    user.save()
                
                # Handle specialization
                specialization = request.POST.get('specialization', '')
                if specialization:
                    user.specialization = specialization
                    user.save()
                
                # Handle services
                services = request.POST.getlist('services', [])
                if services:
                    staff_settings.services.set(services)
            
            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='create',
                entity_type='user',
                entity_id=user.id,
                details=f"Created new {user.get_role_display()} account for {user.get_full_name()}"
            )
            
            messages.success(request, "User created successfully.")
            return redirect('admin_panel:users')
    else:
        form = UserForm()

    # Get all services for staff assignment
    services = Service.objects.filter(is_active=True)

    return render(request, 'admin_panel/user_create_modern.html', {
        'title': 'Create User',
        'form': form,
        'services': services,
    })

@login_required
def admin_user_edit_modern(request, user_id):
    """
    Modern view for editing a user.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the user
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            user = form.save()
            
            # If role is staff, handle staff-specific fields
            if user.role == 'staff':
                # Create or get staff settings
                staff_settings, created = StaffSettings.objects.get_or_create(staff=user)
                
                # Handle bio
                bio = request.POST.get('bio', '')
                if bio:
                    user.bio = bio
                    user.save()
                
                # Handle specialization
                specialization = request.POST.get('specialization', '')
                if specialization:
                    user.specialization = specialization
                    user.save()
                
                # Handle services
                services = request.POST.getlist('services', [])
                if services:
                    staff_settings.services.set(services)
            
            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='update',
                entity_type='user',
                entity_id=user.id,
                details=f"Updated {user.get_role_display()} account for {user.get_full_name()}"
            )
            
            messages.success(request, "User updated successfully.")
            return redirect('admin_panel:users')
    else:
        form = UserEditForm(instance=user_obj)

    # Get staff settings if user is staff
    staff_services = []
    if user_obj.role == 'staff':
        try:
            staff_settings = StaffSettings.objects.get(staff=user_obj)
            staff_services = staff_settings.services.all().values_list('id', flat=True)
        except StaffSettings.DoesNotExist:
            pass

    # Get all services for staff assignment
    services = Service.objects.filter(is_active=True)

    return render(request, 'admin_panel/user_edit_modern.html', {
        'title': 'Edit User',
        'form': form,
        'user_obj': user_obj,
        'services': services,
        'staff_services': staff_services,
    })

@login_required
def admin_staff_create_modern(request):
    """
    Modern view for creating a new staff member.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save()
            
            # Handle services
            services = request.POST.getlist('services', [])
            if services:
                staff_settings = StaffSettings.objects.get(staff=staff)
                staff_settings.services.set(services)
            
            # Handle specialization
            specialization = request.POST.get('specialization', '')
            if specialization:
                staff.specialization = specialization
                staff.save()
            
            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='create',
                entity_type='staff',
                entity_id=staff.id,
                details=f"Created new staff member: {staff.get_full_name()}"
            )
            
            messages.success(request, "Staff member created successfully.")
            return redirect('admin_panel:staff')
    else:
        form = StaffForm()

    # Get all services for staff assignment
    services = Service.objects.filter(is_active=True)

    return render(request, 'admin_panel/staff_create_modern.html', {
        'title': 'Create Staff',
        'form': form,
        'services': services,
    })
