from django.utils import timezone
from pyexpat.errors import messages
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
import requests
from ads.forms import AdsForms
from budgets.models import Orcamento
from notifications.models import Notification
from rankings.forms import AvaliacaoForm
from rankings.models import Avaliacao
from .models import AnuncioImagem, Necessidade
from categories.models import Categoria
from itertools import islice
from django.views.generic import TemplateView
from categories.models import Categoria
from .models import Necessidade

class HomeView(TemplateView):
    template_name = 'home.html'  # Diretamente o nome do arquivo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1) Categorias populares
        categorias_populares = Categoria.objects.order_by('-id')[:24]  # Limita a 24 categorias (2 slides de 12)
        context['categorias_populares'] = [list(islice(categorias_populares, i, i + 12)) for i in range(0, len(categorias_populares), 12)]

        # 2) Anúncios populares (já existente)
        anuncios_populares = Necessidade.objects.exclude(
            status__in=['finalizado', 'cancelado']
        ).order_by('-id')[:8]  # Limita a 8 anúncios para exemplo

        # Divide os anúncios em grupos de 4
        anuncios_grouped = [list(islice(anuncios_populares, i, i + 4)) for i in range(0, len(anuncios_populares), 4)]
        context['anuncios_populares'] = anuncios_grouped

        # 3) Lógica para anúncios com base nas categorias preferidas
        user = self.request.user
        if user.is_authenticated:
            # Verifica se o usuário possui categorias preferidas
            preferred_cats = user.preferred_categories.all()
            if preferred_cats.exists():
                # Se tiver categorias, filtra anúncios ativos nessas categorias, em ordem crescente
                anuncios_preferidos = Necessidade.objects.filter(
                    categoria__in=preferred_cats,
                    status='ativo'
                ).order_by('data_criacao')[:8]  # ou .order_by('titulo'), .order_by('data_criacao'), etc.
            else:
                # Não há categorias preferidas: pega anúncios ativos de forma aleatória
                anuncios_preferidos = Necessidade.objects.filter(
                    status='ativo'
                ).order_by('data_criacao')[:8]  # limite de 4, por exemplo
        else:
            # Usuário não autenticado: exibe também anúncios ativos aleatórios
            anuncios_preferidos = Necessidade.objects.filter(
                status='ativo'
            ).order_by('data_criacao')[:8]

        # Divide os anúncios em grupos de 4
        anuncios_preferidos_grouped = [list(islice(anuncios_preferidos, i, i + 4)) for i in range(0, len(anuncios_preferidos), 4)]
        context['anuncios_preferidos'] = anuncios_preferidos_grouped
        
        # 4) Anúncios próximos (cidade do usuário)
        anuncios_proximos = Necessidade.objects.none()
        anuncios_estado = Necessidade.objects.none()

        if user.is_authenticated and hasattr(user, 'cidade') and user.cidade:
            anuncios_proximos = Necessidade.objects.filter(
                status__in=['ativo', 'em_andamento'],
                cliente__cidade=user.cidade
            ).order_by('-data_criacao')[:5]  # Limite de 5 anúncios

            # Se não houver anúncios na cidade, buscar no estado
            if not anuncios_proximos.exists() and hasattr(user, 'estado') and user.estado:
                anuncios_estado = Necessidade.objects.filter(
                    status__in=['ativo', 'em_andamento'],
                    cliente__estado=user.estado
                ).order_by('-data_criacao')[:5]

        # Divide os anúncios em grupos de 4
        anuncios_proximos_final = anuncios_proximos if anuncios_proximos.exists() else anuncios_estado
        anuncios_proximos_grouped = [list(islice(anuncios_proximos_final, i, i + 4)) for i in range(0, len(anuncios_proximos_final), 4)]
        context['anuncios_proximos'] = anuncios_proximos_grouped

        return context

class NecessidadeListView(ListView):
    model = Necessidade
    template_name = 'necessidade_list.html'
    context_object_name = 'necessidades'

    def get_queryset(self):
        # Filtra as necessidades pelo cliente logado
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

class NecessidadeCreateView(LoginRequiredMixin, CreateView):
    model = Necessidade
    form_class = AdsForms
    template_name = 'necessidade_create.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Salvar a instância principal primeiro
        self.object = form.save(commit=False)
        self.object.cliente = self.request.user
        self.object.ip_usuario = self.get_client_ip()
        self.object.status = 'ativo'
        self.object.save()

        # Processar imagens
        imagens = self.request.FILES.getlist('imagens')
        for img in imagens[:3]:  # Garante o limite máximo
            AnuncioImagem.objects.create(anuncio=self.object, imagem=img)
        
        # Calcula a diferença de dias
        # Usamos data_criacao (DateTimeField, auto_now_add=True) que você tem no model Necessidade
        time_diff = timezone.now() - self.object.data_criacao
        # days_diff = time_diff.days  # Quantos dias inteiros passaram

        # Formata “Há 0 dias” ou “Há 1 dia” ou “Há 2 dias” etc.
        # if days_diff == 0:
        #     dias_str = "Hoje"  # ou "Há menos de 1 dia"
        # elif days_diff == 1:
        #     dias_str = "Há 1 dia"
        # else:
        #     dias_str = f"Há {days_diff} dias"

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
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        necessidade = self.get_object()
        context['show_modal'] = self.request.GET.get('show_modal') == 'True'
       

        # Buscar o orçamento aceito relacionado ao anúncio
        orcamento_aceito = Orcamento.objects.filter(
            anuncio=necessidade, status='aceito').first()

        fornecedor = orcamento_aceito.fornecedor if orcamento_aceito else None
        context['fornecedor'] = fornecedor

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

        # Verificar se o usuário atual já avaliou
        ja_avaliou_usuario_atual = Avaliacao.objects.filter(
            anuncio=necessidade,
            usuario=self.request.user
        ).exists()

        # Passar flags no contexto
        context.update({
            'avaliacao_cliente': avaliacao_cliente,
            'avaliacao_fornecedor': avaliacao_fornecedor,
            'ja_avaliou_usuario_atual': ja_avaliou_usuario_atual,
            'avaliacao_form': AvaliacaoForm(user=self.request.user, anuncio=necessidade),
            'orcamento_aceito': orcamento_aceito
        })

        return context

class NecessidadeUpdateView(UpdateView):
    model = Necessidade
    form_class = AdsForms
    template_name = 'necessidade_update.html'
    # fields = ['categoria', 'titulo', 'descricao', 'quantidade', 'unidade']
    success_url = reverse_lazy('necessidade_list')

class NecessidadeDeleteView(DeleteView):
    model = Necessidade
    template_name = 'necessidade_delete.html'
    success_url = reverse_lazy('necessidade_list')

class FinalizarAnuncioView(LoginRequiredMixin, View):
    """ View para finalizar um anúncio """

    def post(self, request, *args, **kwargs):
        try:
            # Obter o anúncio associado ao cliente logado
            anuncio = get_object_or_404(
                Necessidade, pk=self.kwargs['pk'], cliente=request.user)

            # Verificar se o status do anúncio é "em atendimento"
            if anuncio.status != 'em_atendimento':
                return JsonResponse({'success': False, 'error': 'O anúncio só pode ser finalizado quando está em atendimento.'}, status=400)

            # Verificar se há pelo menos um orçamento com status "aceito"
            orcamento_aceito = anuncio.orcamentos.filter(
                status='aceito').exists()
            if not orcamento_aceito:
                return JsonResponse({'success': False, 'error': 'Não há orçamentos aceitos para este anúncio.'}, status=400)

            # Alterar o status do anúncio para "finalizado"
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
            status__in=['ativo', 'em_andamento']
        ).order_by('-data_criacao')  # Ordena pelos mais recentes

    def get_context_data(self, **kwargs):
        """Adiciona a categoria ao contexto"""
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.categoria
        return context

def enviar_mensagem(request, pk):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        mensagem = request.POST.get('mensagem')
        
        necessidade = Necessidade.objects.get(pk=pk)
        destinatario = necessidade.cliente.email
        
        assunto = f"Contato sobre o anúncio '{necessidade.titulo}' no Necessito.com"
        mensagem_completa = f"De: {nome}\nTelefone: {telefone}\nEmail: {email}\n\n{mensagem}"
        
        send_mail(
            assunto,
            mensagem_completa,
            email,  # Remetente
            [destinatario],  # Destinatário
            fail_silently=False
        )
        
        messages.success(request, 'Mensagem enviada com sucesso!')
        return redirect('necessidade_detail', pk=pk)