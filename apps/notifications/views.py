from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from .models import Notification

@login_required
def notification_list(request):
    """
    View for listing notifications.
    """
    # Get the user's notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Mark all as read if requested
    if request.GET.get('mark_all_read'):
        notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect('notifications:notification_list')

    return render(request, 'notifications/notification_list.html', {
        'title': 'Notifications',
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    })

@login_required
def notification_detail(request, notification_id):
    """
    View for viewing a notification.
    """
    # Get the notification
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    # Mark as read
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

    # Redirect to related object if available
    if notification.related_appointment:
        return redirect('appointments:appointment_detail', appointment_id=notification.related_appointment.id)
    elif notification.related_review:
        return redirect('reviews:review_detail', review_id=notification.related_review.id)

    # If no related object, redirect to notification list
    messages.info(request, "Notification viewed.")
    return redirect('notifications:notification_list')

@login_required
def notification_mark_read(request, notification_id):
    """
    View for marking a notification as read.
    """
    # Get the notification
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    # Mark as read
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()

    # Return JSON response if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # Otherwise redirect to notification list
    messages.success(request, "Notification marked as read.")
    return redirect('notifications:notification_list')

@login_required
def notification_delete(request, notification_id):
    """
    View for deleting a notification.
    """
    # Get the notification
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    # Delete the notification
    notification.delete()

    # Return JSON response if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # Otherwise redirect to notification list
    messages.success(request, "Notification deleted.")
    return redirect('notifications:notification_list')
