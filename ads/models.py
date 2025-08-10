from django.db import models
from django.urls import reverse
from users.models import User
from categories.models import Categoria, SubCategoria
from decimal import Decimal

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
        
    ], default='Unidade'
    )
    marca = models.CharField(max_length=100, blank=True)
    tipo = models.CharField(max_length=100, blank=True)
    bitola = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00, help_text="Ex.: Milímetros")
    compr = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00, help_text="Ex.: Metros")
    peso = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00, help_text="Ex.: Kilogramas")
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
    
    @property
    def result_type(self):
        return 'ads'

    def get_imagem_principal(self):
        """Retorna a primeira imagem do anúncio ou None se não houver imagens"""
        return self.imagens.first()
    
    def get_imagem_principal_url(self):
        """Retorna a URL da primeira imagem ou URL da imagem padrão se não houver imagens"""
        imagem = self.get_imagem_principal()
        if imagem and imagem.imagem:
            return imagem.imagem.url
        # Retorna a URL da imagem padrão se não houver imagens
        return '/static/img/logo_Indicaai_anuncio.png'
    
    def tem_imagens(self):
        """Verifica se o anúncio tem pelo menos uma imagem"""
        return self.imagens.exists()

    def __str__(self):
        return self.titulo
    
class AnuncioImagem(models.Model):
    anuncio = models.ForeignKey('Necessidade', on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='anuncios/%Y/%m/%d/')
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Imagem do Anúncio'
        verbose_name_plural = 'Imagens dos Anúncios'

    def __str__(self):
        return f"Imagem {self.id} - {self.anuncio.titulo}"
