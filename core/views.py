import json
import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.db import connection
from django.core.cache import cache

User = get_user_model()
logger = logging.getLogger(__name__)


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


class SecurityTipsView(TemplateView):
    """View para a página de Dicas de Segurança"""
    template_name = 'security_tips.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '🔒 Dicas de Segurança - Indicaai.com',
            'page_description': 'Mantenha-se seguro na plataforma com nossas dicas essenciais de segurança para negócios online',
            'page_keywords': 'segurança, proteção, golpes, fraudes, dicas, segurança online, negócios seguros',
            'section_name': 'Segurança',
            'section_icon': 'shield-halved',
            'section_color': '#dc3545',
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


class HelpBusinessRulesView(TemplateView):
    """View para a seção 'Regras de Negócio' da central de ajuda"""
    template_name = 'help/help_business_rules.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '📖 Regras de Negócio - Central de Ajuda',
            'page_description': 'Entenda as regras de negócio da plataforma: ciclo de vida dos anúncios, sistema de orçamentos, comunicação e avaliações',
            'page_keywords': 'regras de negócio, anúncios, orçamentos, status, ciclo de vida, disputas, avaliações',
            'section_name': 'Regras de Negócio',
            'section_icon': 'gavel',
            'section_color': '#ffc107',
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


# VIEWS PARA PÁGINAS LEGAIS

class TermsOfServiceView(TemplateView):
    """View para a página de Termos de Uso"""
    template_name = 'legal/termos_de_uso.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Termos de Uso - Indicaai.com',
            'page_description': 'Termos de uso e condições da plataforma Indicaai.com. Leia nossos termos de serviço.',
            'page_keywords': 'termos de uso, condições, serviço, indicaai, plataforma, legal',
            'canonical_url': self.request.build_absolute_uri(),
        })
        return context


class PrivacyPolicyView(TemplateView):
    """View para a página de Política de Privacidade"""
    template_name = 'legal/politica_privacidade.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Política de Privacidade - Indicaai.com',
            'page_description': 'Política de privacidade da Indicaai.com. Como protegemos e utilizamos seus dados pessoais conforme a LGPD.',
            'page_keywords': 'política de privacidade, LGPD, proteção de dados, privacidade, indicaai',
            'canonical_url': self.request.build_absolute_uri(),
        })
        return context


class IntellectualPropertyView(TemplateView):
    """View para a página de Propriedade Intelectual"""
    template_name = 'legal/politica-propriedade-intelectual.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Propriedade Intelectual - Indicaai.com',
            'page_description': 'Política de propriedade intelectual da Indicaai.com. Direitos autorais, marcas e uso de conteúdo.',
            'page_keywords': 'propriedade intelectual, direitos autorais, marcas, copyright, indicaai',
            'canonical_url': self.request.build_absolute_uri(),
        })
        return context


class SitemapView(TemplateView):
    """View para a página do Mapa do Site"""
    template_name = 'sitemap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Mapa do Site - Indicaai.com',
            'page_description': 'Navegue por todas as páginas e funcionalidades da plataforma Indicaai.com. Encontre rapidamente o que você procura.',
            'page_keywords': 'mapa do site, navegação, páginas, indicaai, sitemap, estrutura, ajuda',
            'canonical_url': self.request.build_absolute_uri(),
        })
        return context


# LGPD COMPLIANCE VIEWS

class PrivacyCenterView(TemplateView):
    """Central de Privacidade para gestão de dados pessoais"""
    template_name = 'legal/privacy_center.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's current consent status if logged in
        user_consent = None
        if self.request.user.is_authenticated:
            consent_cookie = self.request.COOKIES.get('lgpd_consent')
            if consent_cookie:
                try:
                    user_consent = json.loads(consent_cookie)
                except json.JSONDecodeError:
                    user_consent = None
        
        context.update({
            'page_title': 'Central de Privacidade - Indicaai.com',
            'page_description': 'Gerencie seus dados pessoais, preferências de cookies e exerça seus direitos de privacidade conforme a LGPD.',
            'page_keywords': 'privacidade, LGPD, dados pessoais, cookies, consentimento, direitos, exclusão',
            'canonical_url': self.request.build_absolute_uri(),
            'user_consent': user_consent,
        })
        return context


class DataExportView(LoginRequiredMixin, TemplateView):
    """View para exportação de dados pessoais"""
    template_name = 'legal/data_export.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Exportar Meus Dados - Indicaai.com',
            'page_description': 'Exporte todos os seus dados pessoais em formato estruturado conforme seus direitos na LGPD.',
            'page_keywords': 'exportar dados, portabilidade, LGPD, dados pessoais',
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Generate and send user data export"""
        try:
            user = request.user
            
            # Collect user data
            user_data = {
                'personal_info': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': getattr(user, 'telefone', ''),
                    'cpf': getattr(user, 'cpf', ''),
                    'cnpj': getattr(user, 'cnpj', ''),
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                },
                'address_info': {
                    'street': getattr(user, 'endereco', ''),
                    'city': getattr(user, 'cidade', ''),
                    'state': getattr(user, 'estado', ''),
                    'cep': getattr(user, 'cep', ''),
                    'neighborhood': getattr(user, 'bairro', ''),
                    'latitude': getattr(user, 'lat', ''),
                    'longitude': getattr(user, 'lon', ''),
                },
                'profile_info': {
                    'bio': getattr(user, 'bio', ''),
                    'photo_url': user.foto.url if hasattr(user, 'foto') and user.foto else '',
                    'email_verified': getattr(user, 'email_verified', False),
                },
                'preferences': {
                    'preferred_categories': [cat.nome for cat in user.preferred_categories.all()] if hasattr(user, 'preferred_categories') else [],
                },
                'export_info': {
                    'export_date': datetime.now().isoformat(),
                    'format': 'JSON',
                    'lgpd_article': 'Art. 18, V - Direito à portabilidade dos dados',
                }
            }
            
            # Create JSON response
            response = JsonResponse(user_data, json_dumps_params={'indent': 2})
            response['Content-Disposition'] = f'attachment; filename="indicaai_dados_{user.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            
            # Log data export request
            logger.info(f"LGPD_DATA_EXPORT: User {user.id} exported personal data")
            
            return response
            
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            messages.error(request, 'Erro ao exportar dados. Tente novamente ou entre em contato com o suporte.')
            return redirect('privacy_center')


class DataDeletionRequestView(LoginRequiredMixin, FormView):
    """View para solicitação de exclusão de dados"""
    template_name = 'legal/data_deletion_request.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Solicitar Exclusão de Dados - Indicaai.com',
            'page_description': 'Solicite a exclusão dos seus dados pessoais conforme seus direitos na LGPD.',
            'page_keywords': 'exclusão dados, delete conta, LGPD, direito esquecimento',
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Process data deletion request"""
        try:
            user = request.user
            reason = request.POST.get('deletion_reason', '')
            confirmation = request.POST.get('confirmation', '') == 'on'
            
            if not confirmation:
                messages.error(request, 'Você deve confirmar que entende as consequências da exclusão.')
                return self.get(request, *args, **kwargs)
            
            # Create deletion request log
            deletion_request = {
                'user_id': user.id,
                'user_email': user.email,
                'request_date': datetime.now().isoformat(),
                'reason': reason,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'status': 'pending_review',
            }
            
            # Log deletion request
            logger.info(f"LGPD_DATA_DELETION_REQUEST: {json.dumps(deletion_request)}")
            
            # Send email notification to support team
            try:
                send_mail(
                    subject='Solicitação de Exclusão de Dados - LGPD',
                    message=f'''
Uma solicitação de exclusão de dados foi recebida:

Usuário ID: {user.id}
Email: {user.email}
Nome: {user.first_name} {user.last_name}
Data da solicitação: {deletion_request['request_date']}
Motivo: {reason}

Esta solicitação deve ser processada em até 15 dias úteis conforme a LGPD.
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['suporteindicaai@hotmail.com'],
                    fail_silently=False,
                )
            except Exception as email_error:
                logger.error(f"Error sending deletion request email: {email_error}")
            
            # Send confirmation email to user
            try:
                send_mail(
                    subject='Solicitação de Exclusão de Dados Recebida - Indicaai.com',
                    message=f'''
Olá {user.first_name},

Recebemos sua solicitação de exclusão de dados pessoais em {deletion_request['request_date']}.

Sua solicitação será processada em até 15 dias úteis conforme estabelecido na Lei Geral de Proteção de Dados (LGPD).

Durante este período:
- Seus dados permanecerão ativos na plataforma
- Você pode cancelar esta solicitação entrando em contato conosco
- Após a confirmação, a exclusão será irreversível

Caso tenha dúvidas, entre em contato com nosso Encarregado de Proteção de Dados através do email suporteindicaai@hotmail.com.

Atenciosamente,
Equipe Indicaai.com
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as user_email_error:
                logger.error(f"Error sending confirmation email to user: {user_email_error}")
            
            messages.success(
                request, 
                'Sua solicitação de exclusão foi recebida e será processada em até 15 dias úteis. '
                'Você receberá uma confirmação por email.'
            )
            
            return redirect('privacy_center')
            
        except Exception as e:
            logger.error(f"Error processing data deletion request: {e}")
            messages.error(request, 'Erro ao processar solicitação. Tente novamente ou entre em contato com o suporte.')
            return self.get(request, *args, **kwargs)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        else:
            return request.META.get('REMOTE_ADDR', '')


@method_decorator(csrf_exempt, name='dispatch')
class LGPDConsentLogView(TemplateView):
    """API endpoint for logging LGPD consent interactions"""
    
    def post(self, request, *args, **kwargs):
        """Log consent interactions for compliance audit"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['timestamp', 'action']
            if not all(field in data for field in required_fields):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            # Get user information
            user_id = None
            if request.user.is_authenticated:
                user_id = request.user.id
            
            # Create log entry
            log_entry = {
                'type': 'consent_interaction',
                'user_id': user_id,
                'session_key': request.session.session_key if hasattr(request, 'session') else None,
                'ip_address': self.get_client_ip(request),
                'interaction_data': data,
                'logged_at': datetime.now().isoformat()
            }
            
            # Log the consent interaction
            logger.info(f"LGPD_CONSENT_INTERACTION: {json.dumps(log_entry)}")
            
            return JsonResponse({'status': 'logged', 'timestamp': log_entry['logged_at']})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error logging consent interaction: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        else:
            return request.META.get('REMOTE_ADDR', '')


class CookiePreferencesView(TemplateView):
    """View for cookie preferences management"""
    template_name = 'legal/cookie_preferences.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current consent status
        consent_cookie = self.request.COOKIES.get('lgpd_consent')
        current_consent = None
        if consent_cookie:
            try:
                current_consent = json.loads(consent_cookie)
            except json.JSONDecodeError:
                current_consent = None
        
        context.update({
            'page_title': 'Preferências de Cookies - Indicaai.com',
            'page_description': 'Configure suas preferências de cookies e gerencie seu consentimento para diferentes tipos de cookies.',
            'page_keywords': 'cookies, preferências, consentimento, LGPD, privacidade',
            'current_consent': current_consent,
        })
        return context


def health_check(request):
    """
    Enhanced health check endpoint for CI/CD pipeline monitoring.
    Returns JSON response with comprehensive system status information.
    """
    import os
    
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check Redis/cache connectivity
    try:
        cache.set('health_check_test', 'ok', 30)
        cache_test = cache.get('health_check_test')
        cache_status = "healthy" if cache_test == 'ok' else "unhealthy"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        cache_status = "unhealthy"
    
    # Check disk space (basic)
    try:
        import shutil
        disk_usage = shutil.disk_usage('/')
        disk_free_gb = disk_usage.free / (1024**3)
        disk_status = "healthy" if disk_free_gb > 1.0 else "warning"  # Warning if < 1GB free
    except Exception:
        disk_status = "unknown"
    
    # Overall status
    critical_checks = [db_status, cache_status]
    overall_status = "healthy" if all(status == "healthy" for status in critical_checks) else "unhealthy"
    
    health_data = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "uptime": os.getenv("CONTAINER_START_TIME", "unknown"),
        "version": getattr(settings, 'VERSION', '1.0.0'),
        "environment": getattr(settings, 'ENVIRONMENT', 'production'),
        "commit_sha": os.getenv("GIT_COMMIT_SHA", "unknown"),
        "build_date": os.getenv("BUILD_DATE", "unknown"),
        "checks": {
            "database": db_status,
            "cache": cache_status,
            "disk_space": disk_status
        },
        "django": {
            "debug": settings.DEBUG,
            "database_engine": settings.DATABASES['default']['ENGINE'],
            "secret_key_configured": bool(settings.SECRET_KEY),
        }
    }
    
    # Return appropriate HTTP status code
    status_code = 200 if overall_status == "healthy" else 503
    
    response = JsonResponse(health_data, status=status_code)
    
    # Add headers for pipeline tracking
    response['X-Health-Status'] = overall_status
    response['X-Commit-SHA'] = os.getenv("GIT_COMMIT_SHA", "unknown")
    response['X-Environment'] = getattr(settings, 'ENVIRONMENT', 'production')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    
    return response