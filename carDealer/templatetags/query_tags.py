from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def query_string(**kwargs):
    query = {k: v for k, v in template.request.GET.items()}
    query.update(kwargs)
    return urlencode(query)