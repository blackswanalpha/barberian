from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from apps.core.models import User
from .models import UserLog

def admin_login(request):
    """
    View for admin login.
    """
    # If user is already logged in and is an admin, redirect to dashboard
    if request.user.is_authenticated and request.user.role == 'admin':
        return redirect('admin_panel:dashboard')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Check if user is an admin
            if user.role == 'admin':
                # Log in the user
                login(request, user)
                
                # Log the login
                UserLog.objects.create(
                    user=user,
                    action='login',
                    entity_type='admin',
                    entity_id=user.id,
                    details=f"Admin login at {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # Redirect to dashboard
                return redirect('admin_panel:dashboard')
            else:
                messages.error(request, "You don't have permission to access the admin panel.")
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'admin_panel/admin_login.html', {
        'title': 'Admin Login',
    })

@login_required
def admin_logout(request):
    """
    View for admin logout.
    """
    # Log the logout
    if request.user.is_authenticated:
        UserLog.objects.create(
            user=request.user,
            action='logout',
            entity_type='admin',
            entity_id=request.user.id,
            details=f"Admin logout at {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    # Log out the user
    logout(request)
    
    # Redirect to login page
    messages.success(request, "You have been logged out successfully.")
    return redirect('admin_panel:admin_login')
