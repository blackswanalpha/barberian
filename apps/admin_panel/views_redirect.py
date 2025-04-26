from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def redirect_to_modern_dashboard(request):
    """
    Redirects to the modern dashboard.
    """
    return redirect('admin_panel:dashboard_modern')
