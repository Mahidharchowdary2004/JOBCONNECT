from django import template
from django.http import QueryDict

register = template.Library()

@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    """
    Allows to manipulate the query string of the current URL.
    Usage:
    {% query_string without='param1' %}
    {% query_string param1=value1 param2=value2 %}
    """
    request = context['request']
    query_dict = request.GET.copy()
    
    # Handle 'without' parameter
    if 'without' in kwargs:
        param_to_remove = kwargs['without']
        if param_to_remove in query_dict:
            del query_dict[param_to_remove]
    
    # Handle adding/modifying parameters
    for key, value in kwargs.items():
        if key != 'without':
            if value is None or value == '':
                if key in query_dict:
                    del query_dict[key]
            else:
                query_dict[key] = value
    
    if not query_dict:
        return ''
    
    return query_dict.urlencode()