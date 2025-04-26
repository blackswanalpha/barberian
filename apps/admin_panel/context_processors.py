from apps.appointments.models import Appointment
from apps.notifications.models import Notification

def admin_context(request):
    """
    Context processor for admin panel.
    """
    context = {}
    
    if request.user.is_authenticated:
        # Get pending notifications
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        notification_count = notifications.count()
        
        # Get pending appointment count for admin users
        if request.user.role == 'admin':
            pending_count = Appointment.objects.filter(status='pending_review').count()
        else:
            pending_count = 0
            
        context.update({
            'notifications': notifications,
            'notification_count': notification_count,
            'pending_count': pending_count,
        })
    
    return context
