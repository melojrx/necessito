"""
Filtros globais para formatação monetária brasileira
Pode ser usado em qualquer template da aplicação
"""
from django import template
from decimal import Decimal, InvalidOperation
import locale

register = template.Library()

@register.filter
def currency_br(value):
    """
    Formata valor como moeda brasileira: R$ 1.234,56
    
    Uso nos templates:
    {% load currency_filters %}
    {{ valor|currency_br }}
    """
    try:
        # Se for None ou vazio, retorna R$ 0,00
        if value is None or value == '':
            return "R$ 0,00"
        
        # Converte para Decimal para garantir precisão
        if isinstance(value, str):
            # Remove caracteres não numéricos exceto pontos e vírgulas
            cleaned = ''.join(c for c in value if c.isdigit() or c in '.,')
            if not cleaned:
                return "R$ 0,00"
            value = cleaned.replace(',', '.')
        
        decimal_value = Decimal(str(value))
        
        # Formata com separador de milhares e casas decimais
        formatted = f"{decimal_value:,.2f}"
        
        # Converte para padrão brasileiro
        # 1,234.56 -> 1.234,56
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return f"R$ {formatted}"
        
    except (ValueError, TypeError, InvalidOperation, ArithmeticError):
        # Em caso de erro, retorna R$ 0,00
        return "R$ 0,00"

@register.filter  
def currency_br_no_symbol(value):
    """
    Formata valor como moeda brasileira sem o símbolo: 1.234,56
    Útil quando o R$ já está no HTML
    """
    result = currency_br(value)
    return result.replace('R$ ', '') if result.startswith('R$ ') else result

@register.filter
def percentage_br(value):
    """
    Formata percentual brasileiro: 12,34%
    """
    try:
        if value is None or value == '':
            return "0,00%"
        
        decimal_value = Decimal(str(value))
        formatted = f"{decimal_value:.2f}".replace('.', ',')
        return f"{formatted}%"
        
    except (ValueError, TypeError, InvalidOperation):
        return "0,00%"

@register.filter
def safe_decimal(value):
    """
    Converte valor para Decimal de forma segura
    """
    try:
        if value is None or value == '':
            return Decimal('0.00')
        return Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        return Decimal('0.00') 