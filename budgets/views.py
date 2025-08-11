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

# Importar os novos decorators e validadores de permissão
from core.decorators import supplier_required
from core.permissions import PermissionValidator
from core.mixins import SupplierRequiredMixin, BudgetOwnerMixin

logger = logging.getLogger(__name__)

@supplier_required
@transaction.atomic
def submeter_orcamento(request, pk):
    """View para submeter orçamento com múltiplos itens"""
    anuncio = get_object_or_404(Necessidade, pk=pk, status__in=['ativo', 'analisando_orcamentos'])
    
    # Validação adicional usando o sistema de permissões
    can_create, message = PermissionValidator.can_create_budget(request.user)
    if not can_create:
        messages.error(request, message)
        return redirect(anuncio.get_absolute_url())
    
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
                anuncio.status = 'analisando_orcamentos'
                anuncio.save(update_fields=['status'])
                logger.info("Status do anúncio alterado para analisando_orcamentos")
            
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

        # Usar o sistema de permissões centralizado
        can_accept, message = PermissionValidator.can_accept_budget(request.user, orcamento)
        if not can_accept:
            return JsonResponse({'error': message}, status=403)

        # Atualiza o status do orçamento e do anúncio
        orcamento.status = 'aceito_pelo_cliente'
        orcamento.save()

        orcamento.anuncio.status = 'aguardando_confirmacao'
        orcamento.anuncio.save(update_fields=['status'])

        messages.success(request, "Orçamento aceito com sucesso!")
        return JsonResponse({'success': True, 'message': 'Orçamento aceito com sucesso!'}) 

class OrcamentoFornecedorAceitarView(LoginRequiredMixin, View):
    """ View para o fornecedor aceitar um orçamento """
    
    def post(self, request, *args, **kwargs):
        orcamento = get_object_or_404(Orcamento, id=self.kwargs['pk'])

        # Verificar se é o fornecedor do orçamento
        if request.user != orcamento.fornecedor:
            return JsonResponse({'error': 'Você não tem permissão para aceitar este orçamento!'}, status=403)

        # Verificar se o orçamento está no status correto
        if orcamento.status != 'aceito_pelo_cliente':
            return JsonResponse({'error': 'Este orçamento não está aguardando confirmação!'}, status=400)

        # Atualiza o status do orçamento e do anúncio
        orcamento.status = 'confirmado'
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

        # Usar o sistema de permissões centralizado
        can_reject, message = PermissionValidator.can_reject_budget(request.user, orcamento)
        if not can_reject:
            return JsonResponse({'error': message}, status=403)

        # Atualiza o status do orçamento para "rejeitado"
        orcamento.status = 'rejeitado'
        orcamento.save()

        messages.success(request, "Orçamento rejeitado com sucesso!")
        return JsonResponse({'success': True, 'message': 'Orçamento rejeitado com sucesso!'})

class budgetListView(SupplierRequiredMixin, ListView):
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

class BudgetUpdateView(SupplierRequiredMixin, UpdateView):
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
        # Validação adicional usando o sistema de permissões
        can_edit, message = PermissionValidator.can_edit_budget(self.request.user, self.object)
        if not can_edit:
            messages.error(self.request, message)
            return redirect('budget_list')
        
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

class budgetDetailView(BudgetOwnerMixin, DetailView):
    model = Orcamento
    template_name = 'budget_detail.html'
    context_object_name = 'orcamento'

class budgetDeleteView(SupplierRequiredMixin, DeleteView):
    model = Orcamento
    template_name = 'budget_delete.html'
    success_url = reverse_lazy('budget_list')

    def get_queryset(self):
        # Filtra os orçamentos pelo fornecedor logado
        return Orcamento.objects.filter(fornecedor=self.request.user)

    def delete(self, request, *args, **kwargs):
        orcamento = self.get_object()

        # Verificar se é o dono do orçamento
        if request.user != orcamento.fornecedor:
            messages.error(request, "Você não tem permissão para excluir este orçamento.")
            return redirect('budget_list')

        # Checa a regra de negócio usando o sistema de permissões
        can_edit, message = PermissionValidator.can_edit_budget(request.user, orcamento)
        if not can_edit:
            messages.error(request, message)
            return redirect('budget_list')

        messages.success(request, "Orçamento excluído com sucesso!")
        return super().delete(request, *args, **kwargs)

# budgets/views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import os

@login_required
def export_orcamento_pdf(request, pk):
    """
    Exporta os detalhes do orçamento como PDF usando xhtml2pdf (temporário)
    """
    orcamento = get_object_or_404(Orcamento, pk=pk)

    # Usar o sistema de permissões centralizado
    can_view, message = PermissionValidator.can_view_budget_details(request.user, orcamento)
    if not can_view:
        return HttpResponse(message, status=403)

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
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="orcamento_{orcamento.id}.pdf"'
            return response
        else:
            return HttpResponse("Erro ao gerar o PDF", status=500)

    except Exception as e:
        return HttpResponse(f"Erro ao gerar PDF: {str(e)}", status=500)