"""
Custom template tags for the calendar modal.
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Look up a key in a dictionary. Usage: {{ mydict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def make_range(value):
    """Generate a range from 1 to value. Usage: {% for i in num|make_range %}"""
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(0)
