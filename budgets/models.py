from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from users.models import User
from ads.models import Necessidade


class Orcamento(models.Model):
    fornecedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orcamentos')
    anuncio = models.ForeignKey(Necessidade, on_delete=models.CASCADE, related_name='orcamentos')

    # Campos do cabeçalho
    prazo_validade = models.DateField()
    prazo_entrega = models.DateField()
    observacao = models.TextField(blank=True)
    arquivo_anexo = models.FileField(upload_to='orcamentos_anexos/', null=True, blank=True)
    
    # Campos de frete e pagamento
    TIPO_FRETE_CHOICES = [
        ('cif', 'CIF (Por conta do fornecedor)'),
        ('fob', 'FOB (Por conta do cliente)'),
        ('sem_frete', 'Sem frete'),
    ]
    tipo_frete = models.CharField(max_length=30, choices=TIPO_FRETE_CHOICES, default='fob')
    valor_frete = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Valor do frete (se aplicável)"
    )
    
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
        ('transferencia', 'Transferência Bancária'),
    ]
    forma_pagamento = models.CharField(max_length=50, choices=FORMA_PAGAMENTO_CHOICES, default='pix')
    
    CONDICAO_PAGAMENTO_CHOICES = [
        ('a_vista', 'À vista'),
        ('entrada_saldo', '50% entrada + 50% na entrega'),
        ('parcelado_2x', 'Parcelado em 2x'),
        ('parcelado_3x', 'Parcelado em 3x'),
        ('parcelado_4x', 'Parcelado em 4x'),
        ('30_dias', '30 dias'),
        ('personalizado', 'Personalizado'),
    ]
    condicao_pagamento = models.CharField(max_length=50, choices=CONDICAO_PAGAMENTO_CHOICES, default='a_vista')
    condicao_pagamento_personalizada = models.TextField(blank=True, help_text="Descreva a condição personalizada")
    
    TIPO_VENDA_CHOICES = [
        ('revenda', 'Revenda'),
        ('uso_consumo', 'Uso e Consumo'),
        ('ativo_imobilizado', 'Ativo Imobilizado'),
        ('servico', 'Serviço'),
    ]
    tipo_venda = models.CharField(max_length=50, choices=TIPO_VENDA_CHOICES, default='uso_consumo')

    STATUS = [
        ('pendente', 'Pendente'),
        ('aguardando', 'Aguardando aceite do fornecedor'),
        ('aceito', 'Aceito'),
        ('rejeitado', 'Rejeitado'),
    ]
    status = models.CharField(max_length=50, choices=STATUS, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def valor_total(self):
        """Calcula o valor total do orçamento baseado nos itens"""
        return self.itens.aggregate(
            total=Sum(F('quantidade') * F('valor_unitario'))
        )['total'] or Decimal('0.00')

    def valor_total_com_impostos(self):
        """Calcula o valor total com impostos aplicados"""
        total = Decimal('0.00')
        for item in self.itens.all():
            total += item.total
        return total

    def clean(self):
        super().clean()
        # Removida a validação incorreta - prazo de entrega pode ser posterior ao prazo de validade
        # O prazo de validade é quando o orçamento expira, não quando o trabalho deve ser entregue

    def __str__(self):
        return f'Orçamento #{self.pk} – {self.fornecedor.get_full_name()}'


class OrcamentoItem(models.Model):
    MATERIAL = 'MAT'
    SERVICO = 'SRV'
    TIPO = [(MATERIAL, 'Material'), (SERVICO, 'Serviço')]

    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name='itens')
    tipo = models.CharField(max_length=3, choices=TIPO)

    # Campos comuns
    descricao = models.CharField(max_length=255)
    quantidade = models.DecimalField(
        max_digits=12, 
        decimal_places=3, 
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    unidade = models.CharField(max_length=10)
    valor_unitario = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # ----------- Específicos de MATERIAL -----------
    ncm = models.CharField(max_length=10, blank=True, help_text="Nomenclatura Comum do Mercosul")
    icms_percentual = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="ICMS em percentual (0-100%)"
    )
    ipi_percentual = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="IPI em percentual (0-100%)"
    )
    st_percentual = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Substituição Tributária em percentual (0-100%)"
    )
    difal_percentual = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="DIFAL em percentual (0-100%)"
    )

    # ----------- Específicos de SERVIÇO ------------
    cnae = models.CharField(max_length=10, blank=True, help_text="Código CNAE do serviço")
    aliquota_iss = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="ISS em percentual (0-100%)"
    )

    @property
    def preco_com_impostos(self):
        """Calcula o preço unitário com impostos aplicados"""
        if self.tipo == self.MATERIAL:
            # Soma todos os percentuais de impostos
            impostos_total = (
                (self.icms_percentual or Decimal('0')) +
                (self.ipi_percentual or Decimal('0')) +
                (self.st_percentual or Decimal('0')) +
                (self.difal_percentual or Decimal('0'))
            )
            multiplicador = Decimal('1') + (impostos_total / Decimal('100'))
            return self.valor_unitario * multiplicador
        elif self.tipo == self.SERVICO:
            # Para serviços, aplica apenas o ISS
            iss = self.aliquota_iss or Decimal('0')
            multiplicador = Decimal('1') + (iss / Decimal('100'))
            return self.valor_unitario * multiplicador
        return self.valor_unitario

    @property
    def total(self):
        """Calcula o valor total do item (quantidade × preço com impostos)"""
        return self.preco_com_impostos * self.quantidade

    @property
    def total_impostos(self):
        """Calcula o valor total dos impostos para este item"""
        return self.total - (self.valor_unitario * self.quantidade)

    def clean(self):
        super().clean()
        if self.tipo == self.MATERIAL:
            if not self.ncm:
                raise ValidationError("NCM é obrigatório para materiais")
        elif self.tipo == self.SERVICO:
            if not self.cnae:
                raise ValidationError("CNAE é obrigatório para serviços")

    def __str__(self):
        return f"{self.descricao} ({self.get_tipo_display()})"
