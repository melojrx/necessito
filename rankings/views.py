from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages
from .models import Avaliacao
from ads.models import Necessidade
from budgets.models import Orcamento  # Importando o modelo correto
from django.utils.timezone import now

class AvaliacaoCreateView(View):
    """Gerencia o registro de avaliações de anúncios"""

    def post(self, request, pk):
        necessidade = get_object_or_404(Necessidade, pk=pk)

        # 🔹 Buscar pelo campo 'anuncio', não 'necessidade'
        orcamento_aceito = Orcamento.objects.filter(anuncio=necessidade, status='aceito').first()
        fornecedor = orcamento_aceito.fornecedor if orcamento_aceito else None

        # Verifica se o usuário é o anunciante ou o fornecedor do orçamento aceito
        if request.user != necessidade.cliente and request.user != fornecedor:
            messages.error(request, 'Você não tem permissão para avaliar este anúncio.')
            return redirect('necessidade_detail', pk=necessidade.pk)

        # Obtém os dados do formulário
        estrelas = request.POST.get('estrelas')

        if not estrelas or not estrelas.isdigit():
            messages.error(request, 'Por favor, selecione uma quantidade válida de estrelas.')
            return redirect('necessidade_detail', pk=necessidade.pk)

        estrelas = int(estrelas)

        # Define quem será avaliado com base no avaliador
        if request.user == necessidade.cliente and fornecedor:
            avaliado = fornecedor
            tipo_avaliacao = 'fornecedor'
        elif request.user == fornecedor:
            avaliado = necessidade.cliente
            tipo_avaliacao = 'cliente'
        else:
            messages.error(request, 'Erro ao processar a avaliação.')
            return redirect('necessidade_detail', pk=necessidade.pk)

        # 🔹 Ajuste: Definir um usuário válido para a avaliação da negociação
        usuario_para_negociacao = fornecedor if request.user == necessidade.cliente else necessidade.cliente

        # ✅ **Verificar se o usuário já avaliou o anúncio**
        avaliacao_existente = Avaliacao.objects.filter(
            usuario=request.user,
            anuncio=necessidade
        ).exists()

        if avaliacao_existente:
            messages.error(request, 'Você já avaliou este anúncio.')
            return redirect('necessidade_detail', pk=necessidade.pk)

        # Registra avaliação para a negociação
        Avaliacao.objects.get_or_create(
            usuario=request.user,
            avaliado=usuario_para_negociacao,
            anuncio=necessidade,
            tipo_avaliacao='negociacao',
            defaults={'estrelas': estrelas, 'data_avaliacao': now()}
        )

        # Registra avaliação para o outro usuário (fornecedor ou cliente)
        Avaliacao.objects.get_or_create(
            usuario=request.user,
            avaliado=avaliado,
            anuncio=necessidade,
            tipo_avaliacao=tipo_avaliacao,
            defaults={'estrelas': estrelas, 'data_avaliacao': now()}
        )

        messages.success(request, 'Sua avaliação foi registrada com sucesso.')
        return redirect('necessidade_detail', pk=necessidade.pk)

