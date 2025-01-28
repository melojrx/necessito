from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from ads.models import Necessidade
from .models import Orcamento
from .forms import OrcamentoForm

class SubmeterOrcamentoView(LoginRequiredMixin, CreateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = 'submeter_orcamento.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obter o anúncio pelo ID passado na URL
        anuncio = get_object_or_404(Necessidade, pk=self.kwargs['pk'], status='ativo')
        context['anuncio'] = anuncio
        return context

    def form_valid(self, form):
        # Obter o anúncio e vincular ao orçamento
        anuncio = get_object_or_404(Necessidade, pk=self.kwargs['pk'], status='ativo')
        form.instance.anuncio = anuncio
        form.instance.fornecedor = self.request.user
        # Replicar os campos do anúncio
        form.instance.descricao = anuncio.descricao
        form.instance.quantidade = anuncio.quantidade
        form.instance.unidade = anuncio.unidade
        form.instance.marca = anuncio.marca
        messages.success(self.request, "Orçamento submetido com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        # Redireciona de volta para os detalhes do anúncio
        return self.object.anuncio.get_absolute_url()

class budgetListView(LoginRequiredMixin, ListView):
    model = Orcamento
    template_name = 'budget_list.html'
    context_object_name = 'orcamentos'

    def get_queryset(self):
        # Filtra os orçamentos pelo fornecedor logado
        queryset = Orcamento.objects.filter(fornecedor=self.request.user).order_by('-data_criacao')

        # Aplica filtro de descrição, se fornecido
        search_query = self.request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(descricao__icontains=search_query)
        
        # Aplica filtro de status, se fornecido
        status_filter = self.request.GET.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = 'budget_update.html'
    success_url = reverse_lazy('budget_list')  # URL da lista de orçamentos

    def get_queryset(self):
        # Filtra os orçamentos pelo fornecedor logado
        return Orcamento.objects.filter(fornecedor=self.request.user)

    def form_valid(self, form):
        # Adiciona uma mensagem de sucesso
        messages.success(self.request, "Orçamento atualizado com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        # Retorna para a lista de orçamentos
        return reverse_lazy('budget_list')

class budgetDetailView(LoginRequiredMixin, DetailView):
    model = Orcamento
    template_name = 'budget_detail.html'
    context_object_name = 'orcamento'

class budgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Orcamento
    template_name = 'budget_delete.html'
    success_url = reverse_lazy('budget_list')

    def get_queryset(self):
        # Filtra os orçamentos pelo fornecedor logado
        queryset = Orcamento.objects.filter(fornecedor=self.request.user)
        return queryset

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Orçamento excluído com sucesso!")
        return super().delete(request, *args, **kwargs)