from django import template
from django.utils.safestring import mark_safe

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
