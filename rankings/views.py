from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
import logging

from rankings.forms import AvaliacaoForm
from .models import Avaliacao, AvaliacaoCriterio
from ads.models import Necessidade
from budgets.models import Orcamento  # Importando o modelo correto
from django.utils.timezone import now

# Configuração de logging para debug
logger = logging.getLogger(__name__)

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
        
        # Verificação crítica: fornecedor deve existir para avaliações
        if not fornecedor:
            messages.error(request, "Não foi possível identificar o fornecedor para avaliação.")
            return redirect("ads:necessidade_detail", pk=necessidade.pk)

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
            # Use template unificado que funciona 100%
            template_name = "avaliacao_form_unified.html"
            return render(request, template_name, context)

        # Renderização convencional da página
        return render(request, "avaliacao_form.html", context)

    def post(self, request, pk):
        """Processa o envio do formulário de avaliação"""
        logger.info(f"POST recebido para avaliação da necessidade {pk} pelo usuário {request.user.id}")
        logger.info(f"Dados POST: {dict(request.POST)}")
        
        necessidade = get_object_or_404(Necessidade, pk=pk)

        # Verifica permissões novamente (mesma lógica do método GET)
        orcamento_aceito = Orcamento.objects.filter(anuncio=necessidade, status='confirmado').first()
        fornecedor = orcamento_aceito.fornecedor if orcamento_aceito else None
        
        # Verificação crítica: fornecedor deve existir
        if not fornecedor:
            logger.error(f"Fornecedor não encontrado para necessidade {pk}")
            messages.error(request, "Não foi possível identificar o fornecedor para avaliação.")
            return redirect("ads:necessidade_detail", pk=necessidade.pk)
            
        # Verificar duplicata antes de processar o formulário
        if Avaliacao.objects.filter(
            usuario=request.user, 
            anuncio=necessidade
        ).exists():
            logger.warning(f"Usuário {request.user.id} tentou avaliar novamente a necessidade {pk}")
            messages.error(request, 'Você já avaliou este anúncio.')
            return redirect('ads:necessidade_detail', pk=necessidade.pk)

        if request.user != necessidade.cliente and request.user != fornecedor:
            logger.warning(f"Usuário {request.user.id} sem permissão para avaliar necessidade {pk}")
            messages.error(request, 'Você não tem permissão para avaliar este anúncio.')
            return redirect('ads:necessidade_detail', pk=necessidade.pk)

        # Define o tipo de avaliação e quem será avaliado
        if request.user == necessidade.cliente:
            tipo_avaliacao = 'fornecedor'
            avaliado = fornecedor
        else:
            tipo_avaliacao = 'cliente'
            avaliado = necessidade.cliente

        logger.info(f"Tipo de avaliação: {tipo_avaliacao}, Avaliado: {avaliado.id}")

        # Cria o formulário com os dados enviados via POST
        form = AvaliacaoForm(
            request.POST,
            user=request.user,
            anuncio=necessidade,
            tipo_avaliacao=tipo_avaliacao
        )

        logger.info(f"Formulário criado. Campos: {list(form.fields.keys())}")
        logger.info(f"Dados limpos: {form.data}")

        if form.is_valid():
            logger.info("Formulário válido, iniciando salvamento com transação")
            
            try:
                with transaction.atomic():
                    # Cria o registro principal da avaliação
                    avaliacao = Avaliacao.objects.create(
                        usuario=request.user,
                        avaliado=avaliado,
                        anuncio=necessidade,
                        tipo_avaliacao=tipo_avaliacao
                    )
                    logger.info(f"Avaliação criada com ID: {avaliacao.id}")

                    # Cria os registros dos critérios de avaliação
                    criterios_salvos = []
                    for field_name, value in form.cleaned_data.items():
                        if field_name.startswith('criterio_'):
                            criterio_key = field_name.replace('criterio_', '')
                            logger.info(f"Salvando critério: {criterio_key} = {value}")
                            
                            # Verificar se o critério é válido
                            criterios_validos = [choice[0] for choice in AvaliacaoCriterio.CRITERIO_CHOICES]
                            if criterio_key not in criterios_validos:
                                logger.error(f"Critério inválido: {criterio_key}")
                                continue
                                
                            criterio = AvaliacaoCriterio.objects.create(
                                avaliacao=avaliacao,
                                criterio=criterio_key,
                                estrelas=int(value)
                            )
                            criterios_salvos.append(criterio)
                            logger.info(f"Critério salvo: {criterio.id}")

                    logger.info(f"Total de critérios salvos: {len(criterios_salvos)}")

                    # Calcula a média das avaliações
                    media = avaliacao.calcular_media()
                    logger.info(f"Média calculada: {media}")

                    messages.success(request, 'Sua avaliação foi registrada com sucesso.')
                    
                    # Se for requisição AJAX, retorna JSON
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': 'Avaliação registrada com sucesso!',
                            'media': float(media) if media else 0,
                            'criterios': len(criterios_salvos)
                        })
                    
                    return redirect('ads:necessidade_detail', pk=necessidade.pk)
                    
            except Exception as e:
                logger.error(f"Erro ao salvar avaliação: {str(e)}")
                messages.error(request, 'Erro interno ao salvar avaliação. Tente novamente.')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Erro interno ao salvar avaliação.',
                        'error': str(e)
                    })

        else:
            # Formulário inválido - log dos erros
            logger.error(f"Formulário inválido. Erros: {form.errors}")
            logger.error(f"Erros não-field: {form.non_field_errors()}")
            
            for field_name, errors in form.errors.items():
                logger.error(f"Campo {field_name}: {errors}")
            
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Formulário inválido',
                    'errors': form.errors
                })

        # Se o formulário for inválido, exibe novamente com os erros
        context = {
            'form': form,
            'necessidade': necessidade,
            'tipo_avaliacao': tipo_avaliacao,
            'avaliado': avaliado
        }

        return render(request, 'avaliacao_form.html', context)


