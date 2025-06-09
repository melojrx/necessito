from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtrai arg de value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def total_impostos(orcamento):
    """Calcula o total de impostos do orçamento"""
    try:
        total_com_impostos = orcamento.valor_total_com_impostos()
        total_sem_impostos = orcamento.valor_total()
        return total_com_impostos - total_sem_impostos
    except:
        return Decimal('0.00') 