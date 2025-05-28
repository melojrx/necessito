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
            'page_title': 'Central de Ajuda - Necessito.com',
            'page_description': 'Central de ajuda da Necessito.com. Aprenda como usar nossa plataforma de oportunidades de negócios, conectar-se com fornecedores e fazer negócios online.',
            'page_keywords': 'ajuda, suporte, como usar, tutorial, necessito, plataforma, negócios, fornecedores',
            'canonical_url': self.request.build_absolute_uri(),
        })
        
        return context


def help_view(request):
    """
    View baseada em função para a página de ajuda.
    Alternativa mais simples à class-based view.
    """
    context = {
        'page_title': 'Central de Ajuda - Necessito.com',
        'page_description': 'Central de ajuda da Necessito.com. Aprenda como usar nossa plataforma de oportunidades de negócios.',
        'page_keywords': 'ajuda, suporte, como usar, tutorial, necessito',
    }
    
    return render(request, 'help/help.html', context) 