from django.utils import timezone
from pyexpat.errors import messages
from itertools import islice
import logging
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger(__name__)
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
import requests
from ads.forms import AdsForms, DisputaForm, DisputaResolverForm
from django.core.mail import send_mail
from budgets.models import Orcamento
from notifications.models import Notification
from rankings.forms import AvaliacaoForm
from rankings.models import Avaliacao
from .models import AnuncioImagem, Necessidade, Disputa
from categories.models import Categoria
from itertools import islice
from django.views.generic import TemplateView
from categories.models import Categoria
from .models import Necessidade
import os
from django.conf import settings
from django.core.files.base import ContentFile

# Importar os novos mixins e validadores de permissão
from core.mixins import ClientRequiredMixin, EmailVerifiedRequiredMixin, AdminRequiredMixin, OwnerRequiredMixin
from core.permissions import PermissionValidator

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ──────────────────────────────────────────────
        # 1) Categorias populares (24 → 2 slides de 12)
        # ──────────────────────────────────────────────
        categorias_populares = Categoria.objects.order_by("-id")[:24]
        context["categorias_populares"] = [
            list(islice(categorias_populares, i, i + 12))
            for i in range(0, len(categorias_populares), 12)
        ]

        # 👇 Adicionado: lista simples para versão mobile adaptada
        context["categorias"] = categorias_populares

        # ──────────────────────────────────────────────
        # 2) Anúncios populares (8 → 2 slides de 4)
        # ──────────────────────────────────────────────
        anuncios_populares = (
            Necessidade.objects.exclude(status__in=["finalizado", "cancelado"])
            .order_by("-data_criacao")[:8]
        )
        context["anuncios_populares"] = [
            list(islice(anuncios_populares, i, i + 4))
            for i in range(0, len(anuncios_populares), 4)
        ]

        # ──────────────────────────────────────────────
        # 3) Anúncios "baseados nas suas categorias"
        #    → agora NUNCA fica vazio
        # ──────────────────────────────────────────────
        user = self.request.user
        qs_preferidos = Necessidade.objects.none()

        if user.is_authenticated:
            preferred_cats = user.preferred_categories.all()
            if preferred_cats.exists():
                qs_preferidos = Necessidade.objects.filter(
                    categoria__in=preferred_cats,
                    status="ativo",
                ).order_by("-data_criacao")[:8]

        if not qs_preferidos.exists():
            qs_preferidos = (
                Necessidade.objects.filter(status="ativo")
                .order_by("data_criacao")[:8]
            )

        context["anuncios_preferidos"] = [
            list(islice(qs_preferidos, i, i + 4))
            for i in range(0, len(qs_preferidos), 4)
        ]

        # ──────────────────────────────────────────────
        # 4) Anúncios próximos (cidade ou estado)
        # ──────────────────────────────────────────────
        anuncios_proximos = Necessidade.objects.none()
        anuncios_estado = Necessidade.objects.none()

        if user.is_authenticated and getattr(user, "cidade", None):
            anuncios_proximos = Necessidade.objects.filter(
                status__in=["ativo", "analisando_orcamentos", "em_atendimento"],
                cliente__cidade=user.cidade,
            ).order_by("-data_criacao")[:5]

            if not anuncios_proximos.exists() and getattr(user, "estado", None):
                anuncios_estado = Necessidade.objects.filter(
                    status__in=["ativo", "analisando_orcamentos", "em_atendimento"],
                    cliente__estado=user.estado,
                ).order_by("-data_criacao")[:5]

        anuncios_final = (
            anuncios_proximos if anuncios_proximos.exists() else anuncios_estado
        )
        context["anuncios_proximos"] = [
            list(islice(anuncios_final, i, i + 4))
            for i in range(0, len(anuncios_final), 4)
        ]

        return context


class NecessidadeListView(ListView):
    model = Necessidade
    template_name = 'necessidade_list.html'
    context_object_name = 'necessidades'

    def get_queryset(self):
        # Filtra as necessidades pelo cliente logado
        if not self.request.user.is_authenticated:
            return Necessidade.objects.none()
        queryset = Necessidade.objects.filter(
            cliente=self.request.user).order_by('-data_criacao')

        # Aplica filtro de descrição, se fornecido
        search_query = self.request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(descricao__icontains=search_query)

        # Aplica filtro de status, se fornecido
        status_filter = self.request.GET.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

class NecessidadeCreateView(ClientRequiredMixin, EmailVerifiedRequiredMixin, CreateView):
    model = Necessidade
    form_class = AdsForms
    template_name = 'necessidade_create_modern.html'
    success_url = reverse_lazy('ads:home')
    
    def get_form_kwargs(self):
        """Passa o usuário para o formulário"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Validação adicional usando o sistema de permissões
        can_create, message = PermissionValidator.can_create_ad(self.request.user)
        if not can_create:
            messages.error(self.request, message)
            return redirect('ads:home')
        
        # Salvar a instância principal primeiro
        self.object = form.save(commit=False)
        self.object.cliente = self.request.user
        self.object.ip_usuario = self.get_client_ip()
        self.object.status = 'ativo'
        self.object.save()

        # Processar imagens
        imagens = self.request.FILES.getlist('imagens')
        
        # Se há imagens enviadas pelo usuário, adicioná-las
        if imagens:
            for img in imagens[:3]:  # Garante o limite máximo de 3 imagens
                AnuncioImagem.objects.create(anuncio=self.object, imagem=img)
        else:
            # Se não há imagens, adicionar a imagem padrão do Indicaai
            self.adicionar_imagem_padrao()
        
        # Calcula a diferença de dias
        # Usamos data_criacao (DateTimeField, auto_now_add=True) que você tem no model Necessidade
        time_diff = timezone.now() - self.object.data_criacao
        # days_diff = time_diff.days  # Quantos dias inteiros passaram

        # Formata "Há 0 dias" ou "Há 1 dia" ou "Há 2 dias" etc.
        # if days_diff == 0:
        #     dias_str = "Hoje"  # ou "Há menos de 1 dia"
        # elif days_diff == 1:
        #     dias_str = "Há 1 dia"
        # else:
        #     dias_str = f"Há {dias_diff} dias"

        # Cria a notificação com HTML embutido
        Notification.objects.create(
            user=self.request.user,
            message=(
                f"<strong>Novo Anúncio Criado</strong><br>"
                # f"<strong>{self.object.titulo}</strong><br>"
                # f"<strong>{self.object.id}</strong><br>"
                # f"<i class='fas fa-clock'></i> {dias_str}"
            ),
            necessidade=self.object
        )

        messages.success(self.request, "Anúncio criado com sucesso!")
        return super().form_valid(form)

    def adicionar_imagem_padrao(self):
        """Adiciona a imagem padrão do Indicaai quando nenhuma imagem é enviada"""
        try:
            # Caminho para a imagem padrão
            imagem_padrao_path = os.path.join(settings.STATIC_ROOT or 'static', 'img', 'logo_Indicaai_anuncio.png')
            
            # Se STATIC_ROOT não estiver definido, usar o diretório static local
            if not os.path.exists(imagem_padrao_path):
                imagem_padrao_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_Indicaai_anuncio.png')
            
            if os.path.exists(imagem_padrao_path):
                with open(imagem_padrao_path, 'rb') as f:
                    imagem_content = f.read()
                
                # Criar uma instância AnuncioImagem com a imagem padrão
                imagem_padrao = AnuncioImagem(anuncio=self.object)
                imagem_padrao.imagem.save(
                    f'anuncio_{self.object.id}_padrao.png',
                    ContentFile(imagem_content),
                    save=True
                )
                
                messages.info(self.request, "Como nenhuma imagem foi enviada, adicionamos uma imagem padrão ao seu anúncio. Você pode editá-lo depois para adicionar suas próprias fotos.")
            
        except Exception as e:
            # Em caso de erro, registrar no log mas não interromper o processo
            print(f"Erro ao adicionar imagem padrão: {e}")
            # O anúncio continua sendo criado mesmo sem imagem

    def get_client_ip(self):
        try:
            response = requests.get("https://api64.ipify.org?format=json", timeout=3)
            return response.json().get("ip", "Desconhecido")
        except Exception:
            return "Desconhecido"

class NecessidadeDetailView(DetailView):
    model = Necessidade
    template_name = 'necessidade_detail.html'
    context_object_name = 'necessidade'
    success_url = reverse_lazy('ads:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        necessidade = self.get_object()
        context['show_modal'] = self.request.GET.get('show_modal') == 'True'

        # Buscar o orçamento confirmado (aceito pelo fornecedor) relacionado ao anúncio
        orcamento_aceito = Orcamento.objects.filter(
            anuncio=necessidade, status='confirmado').first()

        fornecedor = orcamento_aceito.fornecedor if orcamento_aceito else None
        context['fornecedor'] = fornecedor

        # Verificar se o usuário autenticado tem orçamento para esta necessidade
        if self.request.user.is_authenticated:
            usuario_tem_orcamento = Orcamento.objects.filter(
                anuncio=necessidade,
                fornecedor=self.request.user
            ).exists()
            context['usuario_tem_orcamento'] = usuario_tem_orcamento
        else:
            context['usuario_tem_orcamento'] = False

        # Verificar se cliente já avaliou
        avaliacao_cliente = Avaliacao.objects.filter(
            anuncio=necessidade,
            usuario=necessidade.cliente
        ).exists()

        # Verificar se fornecedor já avaliou
        avaliacao_fornecedor = Avaliacao.objects.filter(
            anuncio=necessidade,
            usuario=fornecedor
        ).exists() if fornecedor else False

        # Verificar se o usuário atual já avaliou (só se estiver autenticado)
        if self.request.user.is_authenticated:
            ja_avaliou_usuario_atual = Avaliacao.objects.filter(
                anuncio=necessidade,
                usuario=self.request.user
            ).exists()
            avaliacao_form = AvaliacaoForm(user=self.request.user, anuncio=necessidade)
        else:
            ja_avaliou_usuario_atual = False
            avaliacao_form = None

        # REGRA CRÍTICA: Chat disponível APENAS em status 'em_atendimento' ou 'em_disputa'
        pode_ver_chat = (
            self.request.user.is_authenticated and
            necessidade.status in ['em_atendimento', 'em_disputa'] and
            self.request.user != necessidade.cliente and
            Orcamento.objects.filter(
                anuncio=necessidade, 
                fornecedor=self.request.user
            ).exists()
        )
        
        # Verificar se é o cliente e tem orçamento confirmado
        if (self.request.user.is_authenticated and 
            self.request.user == necessidade.cliente and 
            necessidade.status in ['em_atendimento', 'em_disputa']):
            pode_ver_chat = True
        
        # Passar flags no contexto
        context.update({
            'avaliacao_cliente': avaliacao_cliente,
            'avaliacao_fornecedor': avaliacao_fornecedor,
            'ja_avaliou_usuario_atual': ja_avaliou_usuario_atual,
            'avaliacao_form': avaliacao_form,
            'orcamento_aceito': orcamento_aceito,
            'pode_ver_chat': pode_ver_chat,
            'user_is_owner': self.request.user == necessidade.cliente if self.request.user.is_authenticated else False
        })

        return context

class NecessidadeUpdateView(OwnerRequiredMixin, UpdateView):
    model = Necessidade
    form_class = AdsForms
    template_name = 'necessidade_update.html'
    success_url = reverse_lazy('necessidade_list')
    owner_field = 'cliente'  # Especifica que o campo de propriedade é 'cliente'
    
    def form_valid(self, form):
        # Validação adicional usando o sistema de permissões
        can_edit, message = PermissionValidator.can_edit_ad(self.request.user, self.object)
        if not can_edit:
            messages.error(self.request, message)
            return redirect('necessidade_list')
        
        return super().form_valid(form)

class NecessidadeDeleteView(OwnerRequiredMixin, DeleteView):
    model = Necessidade
    template_name = 'necessidade_delete.html'
    success_url = reverse_lazy('necessidade_list')
    owner_field = 'cliente'  # Especifica que o campo de propriedade é 'cliente'

class FinalizarAnuncioView(LoginRequiredMixin, View):
    """ View para finalizar um anúncio """

    def post(self, request, *args, **kwargs):
        try:
            # Obter o anúncio
            anuncio = get_object_or_404(Necessidade, pk=self.kwargs['pk'])

            # Usar o sistema de permissões centralizado
            can_finalize, message = PermissionValidator.can_finalize_ad(request.user, anuncio)
            if not can_finalize:
                return JsonResponse({'success': False, 'error': message}, status=403)

            # Alterar o status do anúncio para "finalizado" usando state machine
            try:
                anuncio.transition_to('finalizado', user=request.user)
                logger.info(f"Anúncio {anuncio.id} finalizado usando state machine")
            except Exception as e:
                logger.error(f"Erro ao finalizar anúncio usando state machine: {e}")
                # Fallback para método antigo
                anuncio.status = 'finalizado'
                anuncio.save(update_fields=['status'])

            # Retornar resposta JSON indicando sucesso
            return JsonResponse({'success': True, 'message': 'Anúncio finalizado com sucesso!'})

        except Exception as e:
            # Tratar erros inesperados
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

class AnunciosPorCategoriaListView(ListView):
    """Lista os anúncios filtrados por uma categoria específica"""
    model = Necessidade
    template_name = 'anuncios_por_categoria.html'
    context_object_name = 'anuncios'

    def get_queryset(self):
        """Filtra os anúncios pela categoria passada na URL"""
        categoria_id = self.kwargs.get('category_id')
        self.categoria = get_object_or_404(Categoria, id=categoria_id)
        
        return Necessidade.objects.filter(
            categoria=self.categoria,
            status__in=['ativo', 'analisando_orcamentos', 'em_atendimento']
        ).order_by('-data_criacao')  # Ordena pelos mais recentes

    def get_context_data(self, **kwargs):
        """Adiciona a categoria ao contexto"""
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.categoria
        return context
    
from ads.metrics import get_ads_metrics, get_anuncios_criados_vs_finalizados, get_quantidade_anuncios_finalizados_por_categoria, get_quantidade_usuarios_por_tipo, get_valores_metrics, get_valores_por_mes
    
class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Validação adicional usando o sistema de permissões
        can_access, message = PermissionValidator.can_access_dashboard(self.request.user)
        if not can_access:
            messages.error(self.request, message)
            return redirect('ads:home')
        
        context['ads_metrics'] = get_ads_metrics()
        context['valores_metrics'] = get_valores_metrics()
        context['grafico_valores_por_mes'] = get_valores_por_mes()
        context['grafico_categorias'] = get_quantidade_anuncios_finalizados_por_categoria()
        context['grafico_usuarios'] = get_quantidade_usuarios_por_tipo()
        context['grafico_anuncios'] = get_anuncios_criados_vs_finalizados()
        return context

def anuncios_geolocalizados(request):
    anuncios = Necessidade.objects.filter(
        cliente__lat__isnull=False,
        cliente__lon__isnull=False
    ).select_related('cliente')

    print(f"Total de anúncios retornados: {anuncios.count()}")  # 🔍 debug

    data = [{
        'id': anuncio.id,
        'titulo': anuncio.titulo,
        'cidade': anuncio.cliente.cidade,
        'estado': anuncio.cliente.estado,
        'lat': anuncio.cliente.lat,
        'lon': anuncio.cliente.lon,
        'status': anuncio.status,
        'cliente_id': anuncio.cliente.id  
    } for anuncio in anuncios]

    return JsonResponse(data, safe=False)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import requests

User = get_user_model()

@csrf_exempt
def geolocalizar_usuario(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'erro': 'ID de usuário não fornecido'}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'erro': 'Usuário não encontrado'}, status=404)

    if user.lat and user.lon:
        return JsonResponse({'lat': user.lat, 'lon': user.lon})

    # monta endereço
    endereco = f"{user.cidade}, {user.estado}, Brasil"

    try:
        resp = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': endereco, 'format': 'json'}
        )
        data = resp.json()
        if data:
            user.lat = float(data[0]['lat'])
            user.lon = float(data[0]['lon'])
            user.save(update_fields=['lat', 'lon'])
            return JsonResponse({'lat': user.lat, 'lon': user.lon})
        else:
            return JsonResponse({'erro': 'Não encontrado no Nominatim'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)

def enviar_mensagem(request, pk):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        mensagem = request.POST.get('mensagem')
        
        necessidade = Necessidade.objects.get(pk=pk)
        destinatario = necessidade.cliente.email
        
        assunto = f"Contato sobre o anúncio '{necessidade.titulo}' no Indicai.com"
        mensagem_completa = f"De: {nome}\nTelefone: {telefone}\nEmail: {email}\n\n{mensagem}"
        
        send_mail(
            assunto,
            mensagem_completa,
            email,  # Remetente
            [destinatario],  # Destinatário
            fail_silently=False
        )
        
        messages.success(request, 'Mensagem enviada com sucesso!')
        return redirect('ads:necessidade_detail', pk=pk)


def dados_compartilhamento(request, pk):
    """
    View para fornecer dados estruturados de compartilhamento do anúncio.
    Pode ser usada para APIs ou para gerar links personalizados.
    """
    necessidade = get_object_or_404(Necessidade, pk=pk)
    
    # Construir URL completa
    url_completa = request.build_absolute_uri(
        reverse('ads:necessidade_detail', kwargs={'pk': pk})
    )
    
    # Texto estruturado para compartilhamento
    texto_compartilhamento = f"""🔍 Procuro: {necessidade.titulo}

📋 {necessidade.descricao[:150]}{'...' if len(necessidade.descricao) > 150 else ''}
📍 {necessidade.cliente.cidade}, {necessidade.cliente.estado}
💰 Categoria: {necessidade.categoria.nome}
📦 Quantidade: {necessidade.quantidade} {necessidade.unidade}

👆 Acesse o anúncio completo no link:
{url_completa}

#Indicaai #{necessidade.categoria.nome.replace(' ', '')}"""

    dados = {
        'id': necessidade.id,
        'titulo': necessidade.titulo,
        'descricao': necessidade.descricao,
        'categoria': necessidade.categoria.nome,
        'quantidade': necessidade.quantidade,
        'unidade': necessidade.unidade,
        'cidade': necessidade.cliente.cidade,
        'estado': necessidade.cliente.estado,
        'url': url_completa,
        'texto_formatado': texto_compartilhamento,
        'imagem_principal': necessidade.imagens.first().imagem.url if necessidade.imagens.exists() else None,
        'data_criacao': necessidade.data_criacao.strftime('%d/%m/%Y'),
        'status': necessidade.get_status_display()
    }
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(dados)
    
    # Para requisições normais, retorna contexto para template
    return render(request, 'compartilhamento_preview.html', {'dados': dados})


# ==================== VIEWS DE DISPUTAS ====================

class DisputaCreateView(LoginRequiredMixin, CreateView):
    """View para criar uma nova disputa."""
    model = Disputa
    form_class = DisputaForm
    template_name = 'ads/disputa_create.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar permissões antes de processar a requisição."""
        self.necessidade = get_object_or_404(Necessidade, pk=kwargs['necessidade_pk'])
        
        # Verificar se pode abrir disputa
        if not self._pode_abrir_disputa(request.user):
            messages.error(request, "Você não tem permissão para abrir disputa para esta necessidade.")
            return redirect('ads:necessidade_detail', pk=self.necessidade.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def _pode_abrir_disputa(self, user):
        """Verifica se o usuário pode abrir disputa."""
        # Necessidade deve estar em atendimento
        if self.necessidade.status != 'em_atendimento':
            return False
        
        # Usuário deve ser cliente ou fornecedor
        confirmed_budget = self.necessidade.orcamentos.filter(status='confirmado').first()
        if not confirmed_budget:
            return False
        
        if user not in [self.necessidade.cliente, confirmed_budget.fornecedor]:
            return False
        
        # Não deve existir disputa ativa
        active_disputes = self.necessidade.disputas.filter(status__in=['aberta', 'em_analise'])
        if active_disputes.exists():
            return False
        
        return True
    
    def form_valid(self, form):
        """Processar form válido."""
        # Obter orçamento confirmado
        confirmed_budget = self.necessidade.orcamentos.filter(status='confirmado').first()
        if not confirmed_budget:
            messages.error(self.request, "Não foi possível abrir disputa: orçamento confirmado não encontrado.")
            return self.form_invalid(form)
        
        # Configurar instância
        form.instance.necessidade = self.necessidade
        form.instance.orcamento = confirmed_budget
        form.instance.usuario_abertura = self.request.user
        form.instance.ip_usuario_abertura = self._get_client_ip()
        
        try:
            # Salvar disputa (irá atualizar status da necessidade automaticamente)
            response = super().form_valid(form)
            
            messages.success(
                self.request, 
                "Disputa aberta com sucesso. A administração analisará o caso em breve."
            )
            return response
            
        except Exception as e:
            logger.error(f"Erro ao abrir disputa: {e}")
            messages.error(self.request, "Erro ao abrir disputa. Tente novamente.")
            return self.form_invalid(form)
    
    def _get_client_ip(self):
        """Obter IP do cliente."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def get_context_data(self, **kwargs):
        """Adicionar dados ao contexto."""
        context = super().get_context_data(**kwargs)
        context['necessidade'] = self.necessidade
        context['orcamento'] = self.necessidade.orcamentos.filter(status='confirmado').first()
        return context
    
    def get_success_url(self):
        """URL de redirecionamento após sucesso."""
        return reverse('ads:necessidade_detail', kwargs={'pk': self.necessidade.pk})


class DisputaListView(LoginRequiredMixin, ListView):
    """View para listar disputas do usuário."""
    model = Disputa
    template_name = 'ads/disputa_list.html'
    context_object_name = 'disputas'
    paginate_by = 20
    
    def get_queryset(self):
        """Filtrar disputas do usuário."""
        user = self.request.user
        
        # Se é admin, mostrar todas as disputas
        if user.is_staff:
            return (Disputa.objects
                   .select_related('necessidade', 'orcamento', 'usuario_abertura', 'resolvida_por')
                   .prefetch_related('necessidade__orcamentos')
                   .order_by('-data_abertura'))
        
        # Para usuários normais, mostrar apenas disputas relacionadas a eles
        from django.db.models import Q
        
        return (Disputa.objects
               .select_related('necessidade', 'orcamento', 'usuario_abertura', 'resolvida_por')
               .prefetch_related('necessidade__orcamentos')
               .filter(
                   Q(necessidade__cliente=user) |
                   Q(orcamento__fornecedor=user)
               )
               .order_by('-data_abertura'))
    
    def get_context_data(self, **kwargs):
        """Adicionar dados ao contexto."""
        context = super().get_context_data(**kwargs)
        
        # Estatísticas para admins
        if self.request.user.is_staff:
            queryset = self.get_queryset()
            context.update({
                'total_disputas': queryset.count(),
                'disputas_abertas': queryset.filter(status='aberta').count(),
                'disputas_em_analise': queryset.filter(status='em_analise').count(),
                'disputas_resolvidas': queryset.filter(status='resolvida').count(),
                'disputas_urgentes': queryset.filter(
                    status='aberta',
                    data_abertura__lt=timezone.now() - timezone.timedelta(hours=48)
                ).count(),
            })
        
        return context


class DisputaDetailView(LoginRequiredMixin, DetailView):
    """View para visualizar detalhes de uma disputa."""
    model = Disputa
    template_name = 'ads/disputa_detail.html'
    context_object_name = 'disputa'
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar permissões."""
        disputa = self.get_object()
        
        if not disputa.pode_ser_visualizada_por(request.user):
            messages.error(request, "Você não tem permissão para visualizar esta disputa.")
            return redirect('ads:disputa_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Adicionar dados ao contexto."""
        context = super().get_context_data(**kwargs)
        disputa = self.object
        
        context.update({
            'necessidade': disputa.necessidade,
            'orcamento': disputa.orcamento,
            'contraparte': disputa.get_contraparte(self.request.user),
            'tipo_usuario': 'cliente' if self.request.user == disputa.necessidade.cliente else 'fornecedor',
            'pode_resolver': disputa.pode_ser_resolvida_por(self.request.user),
            'pode_cancelar': disputa.pode_ser_cancelada_por(self.request.user),
        })
        
        return context


class DisputaResolverView(AdminRequiredMixin, UpdateView):
    """View para administradores resolverem disputas."""
    model = Disputa
    form_class = DisputaResolverForm
    template_name = 'ads/disputa_resolver.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar se disputa pode ser resolvida."""
        disputa = self.get_object()
        
        if not disputa.pode_ser_resolvida_por(request.user):
            messages.error(request, "Você não tem permissão para resolver esta disputa.")
            return redirect('ads:disputa_detail', pk=disputa.pk)
        
        if disputa.status not in ['aberta', 'em_analise']:
            messages.error(request, "Esta disputa já foi resolvida ou cancelada.")
            return redirect('ads:disputa_detail', pk=disputa.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Processar resolução da disputa."""
        disputa = form.instance
        
        # Validar se status final foi informado quando resolvendo
        if disputa.status == 'resolvida' and not disputa.status_final_necessidade:
            form.add_error('status_final_necessidade', 
                          'Status final da necessidade é obrigatório ao resolver disputa.')
            return self.form_invalid(form)
        
        # Definir quem resolveu
        disputa.resolvida_por = self.request.user
        
        try:
            response = super().form_valid(form)
            messages.success(
                self.request,
                f"Disputa {disputa.get_status_display().lower()} com sucesso."
            )
            return response
            
        except Exception as e:
            logger.error(f"Erro ao resolver disputa {disputa.pk}: {e}")
            messages.error(self.request, "Erro ao processar resolução da disputa.")
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Adicionar dados ao contexto."""
        context = super().get_context_data(**kwargs)
        disputa = self.object
        
        context.update({
            'necessidade': disputa.necessidade,
            'orcamento': disputa.orcamento,
        })
        
        return context
    
    def get_success_url(self):
        """URL após resolver disputa."""
        return reverse('ads:disputa_detail', kwargs={'pk': self.object.pk})


class DisputaCancelarView(LoginRequiredMixin, View):
    """View para cancelar uma disputa."""
    
    def post(self, request, pk):
        """Processar cancelamento da disputa."""
        disputa = get_object_or_404(Disputa, pk=pk)
        
        # Verificar permissões
        if not disputa.pode_ser_cancelada_por(request.user):
            messages.error(request, "Você não tem permissão para cancelar esta disputa.")
            return redirect('ads:disputa_detail', pk=disputa.pk)
        
        if disputa.status != 'aberta':
            messages.error(request, "Apenas disputas abertas podem ser canceladas.")
            return redirect('ads:disputa_detail', pk=disputa.pk)
        
        try:
            # Cancelar disputa
            disputa.status = 'cancelada'
            disputa.save()
            
            # Voltar necessidade para em_atendimento
            state_machine = disputa.necessidade.get_state_machine()
            state_machine.transition_to('em_atendimento', user=request.user)
            
            messages.success(request, "Disputa cancelada com sucesso.")
            
        except Exception as e:
            logger.error(f"Erro ao cancelar disputa {disputa.pk}: {e}")
            messages.error(request, "Erro ao cancelar disputa.")
        
        return redirect('ads:necessidade_detail', pk=disputa.necessidade.pk)