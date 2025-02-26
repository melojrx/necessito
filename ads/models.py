from django.db import models
from django.urls import reverse
from users.models import User
from categories.models import Categoria, SubCategoria

class Necessidade(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="necessidades")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="necessidades")
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, related_name="necessidades")
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    quantidade = models.FloatField()
    medir_no_local = models.BooleanField(default=False)
    unidade = models.CharField(max_length=50, choices=[
        ('un', 'Unidade'),
        ('cx', 'Caixa'),
        ('pc', 'Peça'),
        ('kg', 'Kilograma'),
        ('m', 'Metro'),
        ('m2', 'Metro Quadrado'),
        ('m3', 'Metro Cúbico'),
        ('cm', 'Centímetro'),
        ('mm', 'Milímetro'),
        ('l', 'Litro'),
        ('g', 'Grama'),
        ('h', 'Hora'),
        ('d', 'Dia'),
        ('mês', 'Mês'),
        ('ano', 'Ano'),
        ('m²', 'Metro Quadrado'),
        ('m³', 'Metro Cúbico'),
        ('cm²', 'Centímetro Quadrado'),
        ('cm³', 'Centímetro Cúbico'),
        ('mm²', 'Milímetro Quadrado'),
        ('mm³', 'Milímetro Cúbico'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('g', 'Grama'),
        ('mg', 'Miligrama'),
        ('km', 'Quilograma'),
        ('h', 'Hora'),
        ('d', 'Dia'),
        ('mês', 'Mês'),
        ('ano', 'Ano'),
        
    ], default='un'
    )
    marca = models.CharField(max_length=100, blank=True)
    tipo = models.CharField(max_length=100, blank=True)
    bitola = models.IntegerField(blank=True, default=0.0, help_text="Ex.: Milímetros")
    compr = models.IntegerField(blank=True, default=0.0, help_text="Ex.: Metros")
    peso = models.IntegerField(blank=True, default=0.0, help_text="Ex.: Kilogramas")
    altura = models.FloatField(blank=True, default=0.0, help_text="Ex.: Metros")
    # Status e Rastreamento.
    status = models.CharField(max_length=20, choices=[
        ('ativo', 'Ativo'), # Anúncio ativo e disponível para orçamentos
        ('em_andamento', 'Em andamento'), # Anúncio com orçamento em andamento disparado após o aceite pelo anunciate.
        ('em_atendimento', 'Em atendimento'), # Anúncio com orçamento aceito pelo anunciante e pelo fornecedor. 
        ('finalizado', 'Finalizado'), # Após a entrega do serviço ou produto, o anúncio é finalizado manualmente pelo anunciante.
        ('cancelado', 'Cancelado'), # Anúncio cancelado pelo anunciante.
    ], default='ativo')
    ip_usuario = models.GenericIPAddressField(blank=True, null=True, help_text="Endereço IP do usuário que cadastrou o anúncio")
    duracao = models.CharField(max_length=20, blank=True, null=True, help_text="Duração do serviço ou entrega (ex.: 7 dias, 3 horas)")
    data_criacao = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(blank=True, null=True, auto_now=True)

    def get_absolute_url(self):
        return reverse('necessidade_detail', args=[str(self.pk)])

    def __str__(self):
        return self.titulo
