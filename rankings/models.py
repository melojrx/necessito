from django.db import models
from users.models import User  
from ads.models import Necessidade  

class AvaliacaoCriterio(models.Model):
    """Armazena as avaliações detalhadas por critério específico"""

    avaliacao = models.ForeignKey(
        'Avaliacao',
        on_delete=models.CASCADE,
        related_name='criterios'
    )  # Referência à avaliação principal

    CRITERIO_CHOICES = [
        # Critérios para Cliente
        ('rapidez_respostas', 'Rapidez nas respostas'),
        ('pagamento_acordado', 'Pagamento conforme acordado'),
        ('urbanidade_negociacao', 'Urbanidade na negociação'),

        # Critérios para Fornecedor
        ('qualidade_produto', 'Qualidade do Produto'),
        ('pontualidade_entrega', 'Pontualidade na entrega'),
        ('atendimento', 'Atendimento'),
        ('precos_mercado', 'Preços praticados de acordo com o Mercado'),
    ]

    criterio = models.CharField(
        max_length=30,
        choices=CRITERIO_CHOICES
    )  # Critério avaliado

    estrelas = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)]
    )  # Nota de 1 a 5 estrelas

    class Meta:
        unique_together = ('avaliacao', 'criterio')
        verbose_name = 'Critério de Avaliação'
        verbose_name_plural = 'Critérios de Avaliação'

class Avaliacao(models.Model):
    """Registra avaliações de fornecedores e clientes"""

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='avaliacoes_feitas'
    )  # Usuário que faz a avaliação

    avaliado = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='avaliacoes_recebidas'
    )  # Usuário que está sendo avaliado

    anuncio = models.ForeignKey(
        Necessidade,
        on_delete=models.CASCADE,
        related_name='avaliacoes'
    )  # Anúncio relacionado à avaliação

    TIPO_AVALIACAO_CHOICES = [
        ('fornecedor', 'Fornecedor'),
        ('cliente', 'Cliente'),
    ]

    tipo_avaliacao = models.CharField(
        max_length=20,
        choices=TIPO_AVALIACAO_CHOICES
    )  # Tipo de avaliação (fornecedor ou cliente)

    data_avaliacao = models.DateTimeField(auto_now_add=True)  # Data e hora da avaliação
    media_estrelas = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True
    )  # Média das estrelas atribuídas

    class Meta:
        unique_together = ('usuario', 'avaliado', 'anuncio', 'tipo_avaliacao')
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'

    def calcular_media(self):
        """Calcula a média das estrelas com base nos critérios"""
        criterios = self.criterios.all()
        if criterios:
            total = sum(criterio.estrelas for criterio in criterios)
            self.media_estrelas = total / criterios.count()
            self.save(update_fields=['media_estrelas'])
        return self.media_estrelas
