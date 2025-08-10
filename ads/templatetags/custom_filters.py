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
def count_pendentes(orcamentos):
    """Contar orçamentos pendentes"""
    return orcamentos.filter(status='pendente').count()

@register.filter
def count_aceitos(orcamentos):
    """Contar orçamentos aceitos"""
    return orcamentos.filter(status='aceito').count()

@register.filter
def count_rejeitados(orcamentos):
    """Contar orçamentos rejeitados"""
    return orcamentos.filter(status='rejeitado').count()

@register.filter
def count_aguardando(orcamentos):
    """Contar orçamentos aguardando"""
    return orcamentos.filter(status='aguardando').count()

@register.filter
def imagem_principal_url(anuncio):
    """Retorna a URL da imagem principal do anúncio ou imagem padrão"""
    if anuncio and hasattr(anuncio, 'get_imagem_principal_url'):
        return anuncio.get_imagem_principal_url()
    # Fallback para imagem padrão
    return '/static/img/logo_Indicaai_anuncio.png'

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
        return '/static/img/logo_Indicaai_anuncio.png'
    
    imagens = anuncio.imagens.all()
    if index < len(imagens) and imagens[index].imagem:
        return imagens[index].imagem.url
    
    # Se não há imagem no índice especificado, retornar imagem padrão
    return '/static/img/logo_Indicaai_anuncio.png'