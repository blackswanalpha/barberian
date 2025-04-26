from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import UserLog
from .tailwind_forms import CategoryForm
from apps.services.models import Category

@login_required
def admin_category_create_modern(request):
    """
    Modern view for creating a new category.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('client_portal:home')

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()

            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='create',
                entity_type='category',
                entity_id=category.id,
                details=f"Created new category: {category.name}"
            )

            messages.success(request, "Category created successfully.")
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm()

    return render(request, 'admin_panel/category_create_modern.html', {
        'title': 'Create Category',
        'form': form,
    })

@login_required
def admin_category_edit_modern(request, category_id):
    """
    Modern view for editing a category.
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

            # Log the action
            UserLog.objects.create(
                user=request.user,
                action='update',
                entity_type='category',
                entity_id=category.id,
                details=f"Updated category: {category.name}"
            )

            messages.success(request, "Category updated successfully.")
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin_panel/category_edit_modern.html', {
        'title': 'Edit Category',
        'form': form,
        'category': category,
    })
