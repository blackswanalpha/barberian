from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from apps.core.models import User
from apps.services.models import Service, Category
from apps.staff.models import StaffSettings
from .tailwind_forms import ServiceForm, CategoryForm, StaffForm, StaffEditForm

@login_required
def form_showcase(request):
    """
    View to showcase all redesigned forms.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    return render(request, 'admin_panel/form_showcase.html', {
        'title': 'Form Showcase',
    })

@login_required
def admin_service_create_redesigned(request):
    """
    View for creating a new service with redesigned form.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service created successfully.")
            return redirect('admin_panel:services')
    else:
        form = ServiceForm()

    return render(request, 'admin_panel/service_form_redesigned.html', {
        'title': 'Create Service',
        'form': form,
    })

@login_required
def admin_service_edit_redesigned(request, service_id):
    """
    View for editing a service with redesigned form.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the service
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully.")
            return redirect('admin_panel:services')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'admin_panel/service_form_redesigned.html', {
        'title': 'Edit Service',
        'form': form,
        'service': service,
    })

@login_required
def admin_staff_create_redesigned(request):
    """
    View for creating a new staff member with redesigned form.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member created successfully.")
            return redirect('admin_panel:staff')
    else:
        form = StaffForm()

    return render(request, 'admin_panel/staff_form_redesigned.html', {
        'title': 'Create Staff Member',
        'form': form,
    })

@login_required
def admin_staff_edit_redesigned(request, staff_id):
    """
    View for editing a staff member with redesigned form.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the staff member
    staff = get_object_or_404(User, id=staff_id, role='staff')

    if request.method == 'POST':
        form = StaffEditForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member updated successfully.")
            return redirect('admin_panel:staff')
    else:
        form = StaffEditForm(instance=staff)

    return render(request, 'admin_panel/staff_form_redesigned.html', {
        'title': 'Edit Staff Member',
        'form': form,
        'staff': staff,
    })

@login_required
def admin_category_create_redesigned(request):
    """
    View for creating a new category with redesigned form.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm()

    return render(request, 'admin_panel/category_form_redesigned.html', {
        'title': 'Create Category',
        'form': form,
    })

@login_required
def admin_category_edit_redesigned(request, category_id):
    """
    View for editing a category with redesigned form.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    # Get the category
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin_panel/category_form_redesigned.html', {
        'title': 'Edit Category',
        'form': form,
        'category': category,
    })
