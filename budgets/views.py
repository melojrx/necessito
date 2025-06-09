from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import transaction
from ads.models import Necessidade
from .models import Orcamento
from .forms import OrcamentoForm, ItemFormSet
import logging

logger = logging.getLogger(__name__)

@login_required
@transaction.atomic
def submeter_orcamento(request, pk):
    """View para submeter orçamento com múltiplos itens"""
    anuncio = get_object_or_404(Necessidade, pk=pk, status__in=['ativo', 'em_andamento'])
    
    logger.info(f"submeter_orcamento chamado - Método: {request.method}, Anúncio: {anuncio.id}")
    logger.info(f"Usuário: {request.user}, Autenticado: {request.user.is_authenticated}")

    if request.method == 'POST':
        logger.info("Processando POST request")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        logger.info(f"POST data completo: {dict(request.POST)}")
        
        form = OrcamentoForm(request.POST, request.FILES)
        formset = ItemFormSet(request.POST)
        
        logger.info(f"Form válido: {form.is_valid()}")
        logger.info(f"Formset válido: {formset.is_valid()}")
        
        if not form.is_valid():
            logger.error(f"Erros do form: {form.errors}")
        
        if not formset.is_valid():
            logger.error(f"Erros do formset: {formset.errors}")
            logger.error(f"Erros não-form do formset: {formset.non_form_errors()}")
            # Log detalhado dos erros de cada form no formset
            for i, form_errors in enumerate(formset.errors):
                if form_errors:
                    logger.error(f"Erros do form {i}: {form_errors}")
        
        if form.is_valid() and formset.is_valid():
            logger.info("Ambos formulários válidos, salvando...")
            
            # Salvar o orçamento
            orcamento = form.save(commit=False)
            orcamento.anuncio = anuncio
            orcamento.fornecedor = request.user
            orcamento.save()
            
            logger.info(f"Orçamento salvo com ID: {orcamento.id}")
            
            # Salvar os itens
            formset.instance = orcamento
            itens_salvos = formset.save()
            
            logger.info(f"Itens salvos com sucesso: {len(itens_salvos)} itens")

            # Alterar o status do anúncio SOMENTE se ele ainda estiver "ativo"
            if anuncio.status == 'ativo':
                anuncio.status = 'em_andamento'
                anuncio.save(update_fields=['status'])
                logger.info("Status do anúncio alterado para em_andamento")

            messages.success(request, 'Orçamento submetido com sucesso!')
            logger.info("Redirecionando para detalhes do anúncio")
            return redirect(anuncio.get_absolute_url())
        else:
            logger.error("Formulário ou formset inválido, renderizando novamente")
    else:
        logger.info("Criando formulários vazios para GET request")
        form = OrcamentoForm()
        formset = ItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'anuncio': anuncio
    }
    logger.info("Renderizando template budget_create.html")
    return render(request, 'budget_create.html', context)

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
        orcamento.status = 'aguardando'
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
        if orcamento.anuncio.status != 'em_andamento':
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
            queryset = queryset.filter(itens__descricao__icontains=search_query).distinct()
        
        # Aplica filtro de status, se fornecido
        status_filter = self.request.GET.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Orcamento
    form_class = OrcamentoForm
    template_name = 'budget_update.html'
    success_url = reverse_lazy('budget_list')

    def get_queryset(self):
        # Filtra os orçamentos pelo fornecedor logado
        return Orcamento.objects.filter(fornecedor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ItemFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Orçamento atualizado com sucesso!")
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
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
        return Orcamento.objects.filter(fornecedor=self.request.user)

    def delete(self, request, *args, **kwargs):
        orcamento = self.get_object()

        # Checa a regra de negócio
        if orcamento.status == 'aguardando':
            messages.error(request, "Não é permitido excluir um orçamento aprovado pelo cliente e aguardando seu aceite.")
            return redirect('budget_list')

        messages.success(request, "Orçamento excluído com sucesso!")
        return super().delete(request, *args, **kwargs)

# budgets/views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
import os
from .models import Orcamento

@login_required
def export_orcamento_pdf(request, pk):
    """
    Exporta os detalhes do orçamento como PDF usando xhtml2pdf (temporário)
    """
    orcamento = get_object_or_404(Orcamento, pk=pk)

    # Verificar permissão (apenas o dono do orçamento ou o cliente do anúncio pode exportar)
    if request.user != orcamento.fornecedor and request.user != orcamento.anuncio.cliente:
        return HttpResponse("Acesso negado", status=403)

    # Preparar o contexto para o template
    context = {
        'orcamento': orcamento,
        'now': timezone.now(),
    }

    # Renderizar o template HTML
    html = render_to_string('orcamento_pdf.html', context)

    try:
        # Criar o arquivo PDF usando xhtml2pdf
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            # Se a geração do PDF for bem-sucedida, retornar o PDF como resposta
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"orcamento_{orcamento.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return HttpResponse(f"Erro ao gerar PDF: {pdf.err}", status=500)

    except Exception as e:
        return HttpResponse(f"Erro ao gerar PDF: {str(e)}", status=500)