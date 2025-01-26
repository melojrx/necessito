from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy

from ads.forms import AdsForms
from .models import Necessidade
from categories.models import Categoria

class HomeView(TemplateView):
    template_name = 'home.html'  # Diretamente o nome do arquivo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Buscar as 4 últimas categorias
        context['categorias_populares'] = Categoria.objects.order_by('-id')[:5]
        # Buscar os 3 últimos anúncios (necessidades)
        context['anuncios_populares'] = Necessidade.objects.order_by('-id')[:4]
        return context
    
class NecessidadeListView(ListView):
    model = Necessidade
    template_name = 'necessidade_list.html'
    context_object_name = 'necessidades'
    
    def get_queryset(self):
        # Filtra as necessidades pelo cliente logado
        queryset = Necessidade.objects.filter(cliente=self.request.user).order_by('-data_criacao')
        
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
    template_name = 'necessidade_create.html'
    form_class = AdsForms
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Associa o usuário autenticado ao campo cliente
        form.instance.cliente = self.request.user
        # Captura o IP do usuário
        form.instance.ip_usuario = self.get_client_ip()
        return super().form_valid(form)

    def get_client_ip(self):
        """
        Captura o IP do cliente a partir da requisição.
        """
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class NecessidadeDetailView(DetailView):
    model = Necessidade
    template_name = 'necessidade_detail.html'
    context_object_name = 'necessidade'
    success_url = reverse_lazy('home')

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


