from django import template

register = template.Library()

@register.filter
def batch(iterable, n):
    """
    Batch items in an iterable into lists of size n.
    The last batch may contain fewer than n items.
    
    Usage: {% for batch in items|batch:3 %}
    """
    batch_list = []
    for i in range(0, len(iterable), n):
        batch_list.append(iterable[i:i + n])
    return batch_list