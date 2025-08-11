from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages

from rankings.forms import AvaliacaoForm
from .models import Avaliacao, AvaliacaoCriterio
from ads.models import Necessidade
from budgets.models import Orcamento  # Importando o modelo correto
from django.utils.timezone import now

class AvaliacaoCreateView(View):
    """Gerencia o registro de avaliações de anúncios"""

    def get(self, request, pk):
        """
        Exibe o formulário de avaliação.
        - Se a requisição for AJAX (abertura do modal), devolve só o HTML
          do formulário (`avaliacao_form_modal.html`).
        - Caso contrário, renderiza a página completa
          (`avaliacao_form.html`).
        """
        necessidade = get_object_or_404(Necessidade, pk=pk)

        # ------------------------------------------------------------
        # 1) Verificações de status e permissão
        # ------------------------------------------------------------
        if necessidade.status != "finalizado":
            messages.error(request, "Apenas anúncios finalizados podem ser avaliados.")
            return redirect("ads:necessidade_detail", pk=necessidade.pk)

        orcamento_aceito = Orcamento.objects.filter(
            anuncio=necessidade, status="confirmado"
        ).first()
        fornecedor = orcamento_aceito.fornecedor if orcamento_aceito else None

        if request.user not in (necessidade.cliente, fornecedor):
            messages.error(request, "Você não tem permissão para avaliar este anúncio.")
            return redirect("ads:necessidade_detail", pk=necessidade.pk)

        if Avaliacao.objects.filter(
            usuario=request.user, anuncio=necessidade
        ).exists():
            messages.error(request, "Você já avaliou este anúncio.")
            return redirect("ads:necessidade_detail", pk=necessidade.pk)

        # ------------------------------------------------------------
        # 2) Tipo (cliente ↔ fornecedor) e criação do formulário
        # ------------------------------------------------------------
        if request.user == necessidade.cliente:
            tipo_avaliacao = "fornecedor"
            avaliado = fornecedor
        else:
            tipo_avaliacao = "cliente"
            avaliado = necessidade.cliente

        form = AvaliacaoForm(
            user=request.user,
            anuncio=necessidade,
            tipo_avaliacao=tipo_avaliacao,
        )

        context = {
            "form": form,
            "necessidade": necessidade,
            "tipo_avaliacao": tipo_avaliacao,
            "avaliado": avaliado,
        }

        # ------------------------------------------------------------
        # 3) Saída: fragmento ou página completa
        # ------------------------------------------------------------
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Chamada via fetch() para o modal → devolve SÓ o formulário
            return render(request, "avaliacao_form_modal.html", context)

        # Renderização convencional da página
        return render(request, "avaliacao_form.html", context)

    def post(self, request, pk):
        """Processa o envio do formulário de avaliação"""
        necessidade = get_object_or_404(Necessidade, pk=pk)

        # Verifica permissões novamente (mesma lógica do método GET)
        orcamento_aceito = Orcamento.objects.filter(anuncio=necessidade, status='confirmado').first()
        fornecedor = orcamento_aceito.fornecedor if orcamento_aceito else None

        if request.user != necessidade.cliente and request.user != fornecedor:
            messages.error(request, 'Você não tem permissão para avaliar este anúncio.')
            return redirect('ads:necessidade_detail', pk=necessidade.pk)

        # Define o tipo de avaliação e quem será avaliado
        if request.user == necessidade.cliente:
            tipo_avaliacao = 'fornecedor'
            avaliado = fornecedor
        else:
            tipo_avaliacao = 'cliente'
            avaliado = necessidade.cliente

        # Cria o formulário com os dados enviados via POST
        form = AvaliacaoForm(
            request.POST,
            user=request.user,
            anuncio=necessidade,
            tipo_avaliacao=tipo_avaliacao
        )

        if form.is_valid():
            # Cria o registro principal da avaliação
            avaliacao = Avaliacao.objects.create(
                usuario=request.user,
                avaliado=avaliado,
                anuncio=necessidade,
                tipo_avaliacao=tipo_avaliacao
            )

            # Cria os registros dos critérios de avaliação
            criterios_salvos = []
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('criterio_'):
                    criterio_key = field_name.replace('criterio_', '')
                    criterio = AvaliacaoCriterio.objects.create(
                        avaliacao=avaliacao,
                        criterio=criterio_key,
                        estrelas=value
                    )
                    criterios_salvos.append(criterio)

            # Calcula a média das avaliações
            avaliacao.calcular_media()

            messages.success(request, 'Sua avaliação foi registrada com sucesso.')
            return redirect('ads:necessidade_detail', pk=necessidade.pk)

        # Se o formulário for inválido, exibe novamente com os erros
        context = {
            'form': form,
            'necessidade': necessidade,
            'tipo_avaliacao': tipo_avaliacao,
            'avaliado': avaliado
        }

        return render(request, 'avaliacao_form.html', context)


