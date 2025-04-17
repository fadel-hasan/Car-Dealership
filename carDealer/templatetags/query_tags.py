from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def query_string(context,**kwargs):
    request = context['request']
    query = {k: v for k, v in request.GET.items()}
    query.update(kwargs)
    return urlencode(query)