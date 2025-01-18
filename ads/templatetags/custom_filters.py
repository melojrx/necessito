from django import template
import re

register = template.Library()

@register.filter
def regex_replace(value, pattern):
    """
    Substitui o padrão especificado no valor por uma string vazia.
    """
    return re.sub(pattern, '', value)
