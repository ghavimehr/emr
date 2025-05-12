from django import template
from django.utils.translation import get_language

register = template.Library()

@register.simple_tag
def get_direction():
    """
    Returns 'rtl' if the current language is right-to-left, otherwise 'ltr'.
    """
    rtl_languages = ['fa', 'ar', 'he', 'ur']  # Add any other RTL language codes here
    current_language = get_language()

    if current_language in rtl_languages:
        return 'rtl'
    return 'ltr'

@register.simple_tag
def get_alignment():
    """
    Returns 'text-right' if the current language is right-to-left, otherwise 'text-left'.
    """
    rtl_languages = ['fa', 'ar', 'he', 'ur']
    current_language = get_language()
    if current_language in rtl_languages:
        return 'text-right'
    return 'text-left'
