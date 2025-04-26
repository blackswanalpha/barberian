from django import template
from django.utils.safestring import mark_safe
from apps.services.models import Service

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary.
    """
    return dictionary.get(key)

@register.filter
def format_hour(hour):
    """
    Format an hour (0-23) to a 12-hour format with AM/PM.
    """
    if hour == 0:
        return '12 AM'
    elif hour < 12:
        return f'{hour} AM'
    elif hour == 12:
        return '12 PM'
    else:
        return f'{hour - 12} PM'

@register.filter
def range_hours(value):
    """
    Generate a range of hours from 0 to 23.
    """
    return range(24)

@register.filter
def get_service_price(service_id):
    """
    Get the price of a service by its ID.
    """
    try:
        # Handle ModelChoiceIteratorValue objects
        if hasattr(service_id, 'value'):
            service_id = service_id.value

        service = Service.objects.get(id=service_id)
        return service.price
    except (Service.DoesNotExist, ValueError, TypeError):
        return 0

@register.filter
def get_service_duration(service_id):
    """
    Get the duration of a service by its ID.
    """
    try:
        # Handle ModelChoiceIteratorValue objects
        if hasattr(service_id, 'value'):
            service_id = service_id.value

        service = Service.objects.get(id=service_id)
        return service.duration
    except (Service.DoesNotExist, ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """
    Multiply the value by the argument
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """
    Divide the value by the argument
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def status_color(status):
    """
    Return a Tailwind CSS color class based on appointment status
    """
    status_colors = {
        'pending': 'yellow',
        'pending_review': 'yellow',
        'confirmed': 'green',
        'completed': 'green',
        'cancelled': 'red',
        'no_show': 'gray'
    }
    return status_colors.get(status, 'gray')

@register.filter
def status_icon(status):
    """
    Return a Material icon name based on appointment status
    """
    status_icons = {
        'pending': 'pending',
        'pending_review': 'pending_actions',
        'confirmed': 'event_available',
        'completed': 'check_circle',
        'cancelled': 'cancel',
        'no_show': 'event_busy'
    }
    return status_icons.get(status, 'help')
