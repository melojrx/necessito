from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
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
        anuncio = get_object_or_404(Necessidade, pk=self.kwargs['pk'], status__in=['ativo', 'em_andamento'])
        context['anuncio'] = anuncio
        return context

    def form_valid(self, form):
        # Obter o anúncio e vincular ao orçamento
        anuncio = get_object_or_404(Necessidade, pk=self.kwargs['pk'], status__in=['ativo', 'em_andamento'])
        form.instance.anuncio = anuncio
        form.instance.fornecedor = self.request.user

        # Replicar os campos do anúncio
        form.instance.descricao = anuncio.descricao
        form.instance.quantidade = anuncio.quantidade
        form.instance.unidade = anuncio.unidade
        form.instance.marca = anuncio.marca

        # Alterar o status do anúncio SOMENTE se ele ainda estiver "ativo"
        if anuncio.status == 'ativo':
            anuncio.status = 'em_andamento'
            anuncio.save(update_fields=['status'])  # Atualiza apenas o campo status

        messages.success(self.request, "Orçamento submetido com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        # Redireciona de volta para os detalhes do anúncio
        return self.object.anuncio.get_absolute_url()

class OrcamentoAceitarView(LoginRequiredMixin, View):
    """ View para o anunciante aceitar um orçamento """
    
    def post(self, request, *args, **kwargs):
        orcamento = get_object_or_404(Orcamento, id=self.kwargs['pk'])

        # Verifica se o orçamento ainda está pendente
        if orcamento.status != 'pendente':
            return JsonResponse({'error': 'Este orçamento já foi processado e não pode mais ser aceito!'}, status=400)

        # Verifica se o usuário logado é o dono do anúncio
        if request.user != orcamento.anuncio.cliente:
            return JsonResponse({'error': 'Você não tem permissão para aceitar este orçamento!'}, status=403)

        # Atualiza o status do orçamento e mantém o status do anúncio
        orcamento.status = 'aguardando_aceite_fornecedor'
        orcamento.save()

        orcamento.anuncio.status = 'em_andamento'
        orcamento.anuncio.save(update_fields=['status'])

        messages.success(request, "Orçamento aceito com sucesso!")
        return JsonResponse({'success': True, 'message': 'Orçamento aceito com sucesso!'}) 

class OrcamentoFornecedorAceitarView(LoginRequiredMixin, View):
    """ View para o fornecedor aceitar um orçamento """
    
    def post(self, request, *args, **kwargs):
        orcamento = get_object_or_404(Orcamento, id=self.kwargs['pk'])

        # Verifica se o usuário logado é o fornecedor do orçamento
        if request.user != orcamento.fornecedor:
            return JsonResponse({'error': 'Você não tem permissão para aceitar este orçamento!'}, status=403)

        # Atualiza o status do orçamento para "aceito"
        orcamento.status = 'aceito'
        orcamento.save()

        # Atualiza o status do anúncio para "em_atendimento"
        orcamento.anuncio.status = 'em_atendimento'
        orcamento.anuncio.save(update_fields=['status'])

        messages.success(request, "Orçamento aceito pelo fornecedor com sucesso!")
        return JsonResponse({'success': True, 'message': 'Orçamento aceito com sucesso!'})

class OrcamentoRejeitarView(LoginRequiredMixin, View):
    """ View para o dono do anúncio rejeitar um orçamento """

    def post(self, request, *args, **kwargs):
        orcamento = get_object_or_404(Orcamento, id=self.kwargs['pk'])

        # Verifica se o orçamento ainda está pendente
        if orcamento.status != 'pendente':
            return JsonResponse({'error': 'Este orçamento já foi processado e não pode mais ser rejeitado!'}, status=400)

        # Verifica se o usuário logado é o dono do anúncio
        if request.user != orcamento.anuncio.cliente:
            return JsonResponse({'error': 'Você não tem permissão para rejeitar este orçamento!'}, status=403)

        # Verifica se o anúncio está em andamento
        if orcamento.anuncio.status == 'em_andamento' or 'Em andamento':
            return JsonResponse({'error': 'Você só pode rejeitar orçamentos enquanto o anúncio está em andamento!'}, status=400)

        # Atualiza o status do orçamento para "rejeitado"
        orcamento.status = 'rejeitado'
        orcamento.save()

        messages.success(request, "Orçamento rejeitado com sucesso!")
        return JsonResponse({'success': True, 'message': 'Orçamento rejeitado com sucesso!'})

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

# budgets/views.py
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
import os
from .models import Orcamento

@login_required
def export_orcamento_pdf(request, pk):
    """
    Exporta os detalhes do orçamento como PDF (versão simplificada sem logo)
    """
    orcamento = Orcamento.objects.get(pk=pk)

    # Verificar permissão (apenas o dono do orçamento ou o cliente do anúncio pode exportar)
    if request.user != orcamento.fornecedor and request.user != orcamento.anuncio.cliente:
        return HttpResponse("Acesso negado", status=403)

    # Preparar o contexto para o template
    context = {
        'orcamento': orcamento,
        'now': timezone.now(),  # Data e hora atual
    }

    # Renderizar o template HTML
    template = get_template('orcamento_pdf.html')
    html = template.render(context)

    # Criar o arquivo PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        # Se a geração do PDF for bem-sucedida, retornar o PDF como resposta
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"orcamento_{orcamento.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return HttpResponse("Erro ao gerar PDF", status=500)