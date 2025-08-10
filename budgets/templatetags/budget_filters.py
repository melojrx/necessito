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

@register.filter
def currency_format(value):
    """Formata valor como moeda brasileira"""
    try:
        if value is None:
            return "R$ 0,00"
        value = Decimal(str(value))
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError, AttributeError):
        return "R$ 0,00"

@register.filter
def safe_decimal(value):
    """Converte valor para Decimal de forma segura"""
    try:
        if value is None or value == '':
            return Decimal('0.00')
        return Decimal(str(value))
    except (ValueError, TypeError, AttributeError):
        return Decimal('0.00')

@register.filter
def multiply(value, arg):
    """Multiplica value por arg"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return Decimal('0.00') 