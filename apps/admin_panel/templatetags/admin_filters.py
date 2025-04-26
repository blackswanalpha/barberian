from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def abs_value(value):
    """Returns the absolute value"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0

@register.filter
def replace_underscore(value):
    """Replaces all underscores with spaces"""
    if value is None:
        return ""

    return str(value).replace("_", " ")

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary using the key"""
    import json

    if dictionary is None:
        return None

    # If dictionary is a string (JSON), try to parse it
    if isinstance(dictionary, str):
        try:
            dictionary = json.loads(dictionary)
        except json.JSONDecodeError:
            return None

    # Now dictionary should be a dict, use get method
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))

    return None
