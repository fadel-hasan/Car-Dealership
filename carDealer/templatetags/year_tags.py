from django import template
from datetime import datetime

register = template.Library()

@register.simple_tag
def current_year():
    """Returns the current year"""
    return datetime.now().year