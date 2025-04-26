from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from apps.core.models import User
from apps.services.models import Service, Category
from apps.staff.models import StaffSettings
from .tailwind_forms_updated import ServiceForm, CategoryForm, StaffFormNoPassword

@login_required
def admin_staff_create_updated(request):
    """
    View for creating a new staff member with updated form (no username/password).
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = StaffFormNoPassword(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save()
            messages.success(request, f"Staff member {staff.get_full_name()} created successfully with a random password. They will need to use the password reset feature to set their own password.")
            return redirect('admin_panel:staff')
    else:
        form = StaffFormNoPassword()

    return render(request, 'admin_panel/staff_form_updated.html', {
        'title': 'Create Staff Member',
        'form': form,
    })

@login_required
def admin_staff_edit_updated(request, staff_id):
    """
    View for editing a staff member with updated form (no username/password).
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the staff member
    staff = get_object_or_404(User, id=staff_id, role='staff')

    if request.method == 'POST':
        form = StaffFormNoPassword(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f"Staff member {staff.get_full_name()} updated successfully.")
            return redirect('admin_panel:staff')
    else:
        form = StaffFormNoPassword(instance=staff)

    return render(request, 'admin_panel/staff_form_updated.html', {
        'title': 'Edit Staff Member',
        'form': form,
        'staff': staff,
    })

@login_required
def form_showcase_updated(request):
    """
    View to showcase all updated forms.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    return render(request, 'admin_panel/form_showcase.html', {
        'title': 'Updated Form Showcase',
    })
