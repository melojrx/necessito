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
def moeda_brasileira(valor):
    try:
        valor = float(valor)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return valor