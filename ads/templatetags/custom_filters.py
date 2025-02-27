from django import template
import locale
import re

register = template.Library()

@register.filter
def regex_replace(value, pattern):
    """
    Substitui o padrão especificado no valor por uma string vazia.
    """
    return re.sub(pattern, '', value)

@register.filter
def moeda_brasileira(value):
    """Formata um valor como moeda brasileira (R$ 1.234,56)."""
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Define localidade para Brasil
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')  # Usa configuração padrão se não suportado
    
    return locale.currency(value, grouping=True, symbol="R$ ") if value else "R$ 0,00"
