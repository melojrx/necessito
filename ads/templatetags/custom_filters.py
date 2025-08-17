from django import template
import locale
import re
from decimal import Decimal

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

@register.filter
def currency(value):
    """Formatar valores monetários em reais"""
    if value is None or value == '':
        return 'R$ 0,00'
    
    try:
        if isinstance(value, str):
            value = Decimal(value)
        elif not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        # Formatar com separadores brasileiros
        formatted = f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f'R$ {formatted}'
    except (ValueError, TypeError):
        return 'R$ 0,00'

@register.filter
def count_orcamentos_by_status(orcamentos, status):
    """Contar orçamentos por status específico"""
    return orcamentos.filter(status=status).count()

@register.filter
def count_enviados(orcamentos):
    """Contar orçamentos enviados"""
    return orcamentos.filter(status='enviado').count()

@register.filter
def count_aceitos_pelo_cliente(orcamentos):
    """Contar orçamentos aceitos pelo cliente"""
    return orcamentos.filter(status='aceito_pelo_cliente').count()

@register.filter
def count_rejeitados_pelo_cliente(orcamentos):
    """Contar orçamentos rejeitados pelo cliente"""
    return orcamentos.filter(status='rejeitado_pelo_cliente').count()

@register.filter
def count_confirmados(orcamentos):
    """Contar orçamentos confirmados (aceitos pelo fornecedor)"""
    return orcamentos.filter(status='confirmado').count()

@register.filter
def count_recusados_pelo_fornecedor(orcamentos):
    """Contar orçamentos recusados pelo fornecedor"""
    return orcamentos.filter(status='recusado_pelo_fornecedor').count()

@register.filter
def status_badge_class(status):
    """Retorna a classe CSS para o badge de status do orçamento"""
    status_classes = {
        'enviado': 'bg-secondary',
        'aceito_pelo_cliente': 'bg-warning text-dark',
        'confirmado': 'bg-success',
        'rejeitado_pelo_cliente': 'bg-danger',
        'recusado_pelo_fornecedor': 'bg-danger',
    }
    return status_classes.get(status, 'bg-secondary')

@register.filter
def order_by_status(orcamentos):
    """Ordena orçamentos por status (enviado primeiro, depois aceito pelo cliente, etc.)"""
    status_order = {
        'enviado': 1,
        'aceito_pelo_cliente': 2,
        'confirmado': 3,
        'rejeitado_pelo_cliente': 4,
        'recusado_pelo_fornecedor': 5,
    }
    
    def get_status_order(orcamento):
        return status_order.get(orcamento.status, 99)
    
    return sorted(orcamentos, key=get_status_order)

@register.filter
def imagem_principal_url(anuncio):
    """Retorna a URL da imagem principal do anúncio ou imagem padrão"""
    if anuncio and hasattr(anuncio, 'get_imagem_principal_url'):
        return anuncio.get_imagem_principal_url()
    # Fallback para imagem padrão
    return '/static/img/logo_Indicaai_anuncio.svg'

@register.filter
def tem_imagens_proprias(anuncio):
    """Verifica se o anúncio tem imagens próprias (não apenas a padrão)"""
    if not anuncio or not hasattr(anuncio, 'imagens'):
        return False
    
    # Se tem mais de uma imagem, certamente tem imagens próprias
    if anuncio.imagens.count() > 1:
        return True
    
    # Se tem apenas uma imagem, verificar se não é a padrão
    primeira_imagem = anuncio.imagens.first()
    if primeira_imagem and primeira_imagem.imagem:
        # Verificar se o nome do arquivo não contém 'padrao'
        return 'padrao' not in primeira_imagem.imagem.name.lower()
    
    return False

@register.simple_tag
def imagem_anuncio_url(anuncio, index=0):
    """Retorna a URL da imagem do anúncio no índice especificado ou imagem padrão"""
    if not anuncio or not hasattr(anuncio, 'imagens'):
        return '/static/img/logo_Indicaai_anuncio.svg'
    
    imagens = anuncio.imagens.all()
    if index < len(imagens) and imagens[index].imagem:
        return imagens[index].imagem.url
    
    # Se não há imagem no índice especificado, retornar imagem padrão
    return '/static/img/logo_Indicaai_anuncio.svg'