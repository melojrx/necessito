from django.views.generic.edit import CreateView
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
