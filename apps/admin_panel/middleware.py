from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve, reverse
from django.conf import settings

class AdminAuthenticationMiddleware:
    """
    Middleware to ensure only admin users can access the admin panel.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current URL path
        path = request.path_info
        
        # Check if the path starts with the admin panel URL
        if path.startswith('/admin_panel/'):
            # Skip authentication check for login page
            if path == reverse('admin_panel:admin_login'):
                return self.get_response(request)
                
            # Check if user is authenticated
            if not request.user.is_authenticated:
                messages.error(request, "Please log in to access the admin panel.")
                return redirect('admin_panel:admin_login')
                
            # Check if user is an admin
            if request.user.role != 'admin':
                messages.error(request, "You don't have permission to access the admin panel.")
                return redirect('client_portal:home')
        
        # Continue with the request
        return self.get_response(request)
