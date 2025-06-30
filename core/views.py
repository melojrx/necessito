from django.shortcuts import render
from django.views.generic import TemplateView


class HelpView(TemplateView):
    """
    View para a página de ajuda/suporte da plataforma.
    
    Fornece informações sobre como usar a plataforma,
    etapas do processo e outras informações úteis.
    """
    template_name = 'help/help.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dados para SEO
        context.update({
            'page_title': 'Central de Ajuda - Indicaai.com',
            'page_description': 'Central de ajuda da Indicaai.com. Aprenda como usar nossa plataforma de oportunidades de negócios, conectar-se com fornecedores e fazer negócios online.',
            'page_keywords': 'ajuda, suporte, como usar, tutorial, indicaai, plataforma, negócios, fornecedores',
            'canonical_url': self.request.build_absolute_uri(),
        })
        
        return context


# VIEWS ESPECÍFICAS PARA CADA SEÇÃO DA CENTRAL DE AJUDA

class HelpStartView(TemplateView):
    """View para a seção 'Começar' da central de ajuda"""
    template_name = 'help/comecar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '🚀 Começar - Central de Ajuda',
            'page_description': 'Primeiros passos na plataforma e configuração inicial da conta',
            'page_keywords': 'começar, criar conta, perfil, configuração inicial, primeiros passos',
            'section_name': 'Começar',
            'section_icon': 'rocket',
            'section_color': '#28a745',
        })
        return context


class HelpAnnounceView(TemplateView):
    """View para a seção 'Anunciar' da central de ajuda"""
    template_name = 'help/anunciar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '💼 Anunciar - Central de Ajuda',
            'page_description': 'Aprenda a criar anúncios eficazes e atrair fornecedores qualificados',
            'page_keywords': 'anunciar, criar anúncios, fotos, categorias, gerenciar anúncios',
            'section_name': 'Anunciar',
            'section_icon': 'bullhorn',
            'section_color': '#0d6efd',
        })
        return context


class HelpBudgetView(TemplateView):
    """View para a seção 'Orçamentos' da central de ajuda"""
    template_name = 'help/orcamentos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '💰 Orçamentos - Central de Ajuda',
            'page_description': 'Solicite, envie e gerencie orçamentos de forma profissional',
            'page_keywords': 'orçamentos, propostas, negociação, valores, aprovação',
            'section_name': 'Orçamentos',
            'section_icon': 'calculator',
            'section_color': '#ffc107',
        })
        return context


class HelpCommunicationView(TemplateView):
    """View para a seção 'Comunicação' da central de ajuda"""
    template_name = 'help/comunicacao.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '💬 Comunicação - Central de Ajuda',
            'page_description': 'Use o chat integrado para negociar e esclarecer dúvidas',
            'page_keywords': 'chat, comunicação, arquivos, etiqueta, denúncias',
            'section_name': 'Comunicação',
            'section_icon': 'comments',
            'section_color': '#17a2b8',
        })
        return context


class HelpRatingsView(TemplateView):
    """View para a seção 'Avaliações' da central de ajuda"""
    template_name = 'help/avaliacoes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '⭐ Avaliações - Central de Ajuda',
            'page_description': 'Sistema de reputação e como avaliar experiências',
            'page_keywords': 'avaliações, reputação, estrelas, credibilidade, fornecedores',
            'section_name': 'Avaliações',
            'section_icon': 'star',
            'section_color': '#fd7e14',
        })
        return context


class HelpSupportView(TemplateView):
    """View para a seção 'Suporte' da central de ajuda"""
    template_name = 'help/suporte.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '🔧 Suporte - Central de Ajuda',
            'page_description': 'Problemas técnicos, políticas e contato direto',
            'page_keywords': 'suporte, problemas técnicos, políticas, privacidade, contato',
            'section_name': 'Suporte',
            'section_icon': 'headset',
            'section_color': '#6f42c1',
        })
        return context


def help_view(request):
    """
    View baseada em função para a página de ajuda.
    Alternativa mais simples à class-based view.
    """
    context = {
        'page_title': 'Central de Ajuda - Indicaai.com',
        'page_description': 'Central de ajuda da Indicaai.com. Aprenda como usar nossa plataforma de oportunidades de negócios.',
        'page_keywords': 'ajuda, suporte, como usar, tutorial, indicaai',
    }
    
    return render(request, 'help/help.html', context) 