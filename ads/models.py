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
    status = models.CharField(max_length=30, choices=[
        ('ativo', 'Ativo'), # Anúncio ativo e disponível para orçamentos
        ('analisando_orcamentos', 'Analisando orçamentos'), # Já recebeu pelo menos um orçamento. O cliente está analisando as propostas.
        ('aguardando_confirmacao', 'Aguardando confirmação'), # Cliente aceitou um orçamento. Aguardando a confirmação do fornecedor.
        ('em_andamento', 'Em andamento'), # Anúncio com orçamento em andamento disparado após o aceite pelo anunciate.
        ('em_atendimento', 'Em atendimento'), # Anúncio com orçamento aceito pelo anunciante e pelo fornecedor. 
        ('finalizado', 'Finalizado'), # Após a entrega do serviço ou produto, o anúncio é finalizado manualmente pelo anunciante.
        ('cancelado', 'Cancelado'), # Anúncio cancelado pelo anunciante.
    ], default='ativo')
    ip_usuario = models.GenericIPAddressField(blank=True, null=True, help_text="Endereço IP do usuário que cadastrou o anúncio")
    duracao = models.CharField(max_length=20, blank=True, null=True, help_text="Duração do serviço ou entrega (ex.: 7 dias, 3 horas)")
    
    # ==================== CAMPOS DE ENDEREÇO DO SERVIÇO ====================
    usar_endereco_usuario = models.BooleanField(
        "Usar meu endereço", 
        default=True,
        help_text="Marque se o serviço será executado no seu endereço cadastrado"
    )
    
    # Endereço específico do serviço (quando diferente do usuário)
    cep_servico = models.CharField(
        "CEP do local do serviço", 
        max_length=10, 
        blank=True,
        help_text="Apenas números: 01234567"
    )
    endereco_servico = models.CharField(
        "Logradouro", 
        max_length=200, 
        blank=True,
        help_text="Rua, Avenida, etc."
    )
    numero_servico = models.CharField(
        "Número", 
        max_length=10, 
        blank=True
    )
    complemento_servico = models.CharField(
        "Complemento", 
        max_length=100, 
        blank=True,
        help_text="Apartamento, sala, etc."
    )
    bairro_servico = models.CharField(
        "Bairro do serviço", 
        max_length=100, 
        blank=True
    )
    cidade_servico = models.CharField(
        "Cidade do serviço", 
        max_length=100, 
        blank=True
    )
    estado_servico = models.CharField(
        "Estado (UF) do serviço",
        max_length=2,
        blank=True,
        help_text="Ex: SP, RJ, MG"
    )
    
    # Coordenadas do local do serviço
    lat_servico = models.FloatField("Latitude do serviço", null=True, blank=True)
    lon_servico = models.FloatField("Longitude do serviço", null=True, blank=True)
    
    # Campo para armazenar dados completos da API
    endereco_completo_json = models.JSONField(
        "Dados completos do endereço", 
        null=True, 
        blank=True,
        help_text="Dados retornados pela API de CEP/Geocoding"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(blank=True, null=True, auto_now=True)

    def get_absolute_url(self):
        return reverse('ads:necessidade_detail', args=[str(self.pk)])
    
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
    
    # ==================== MÉTODOS DE ENDEREÇO ====================
    
    def get_endereco_completo(self):
        """Retorna endereço completo formatado do local do serviço"""
        if self.usar_endereco_usuario:
            return self.cliente.get_endereco_completo() if hasattr(self.cliente, 'get_endereco_completo') else f"{self.cliente.cidade}, {self.cliente.estado}"
        
        # Montar endereço do serviço
        partes = []
        if self.endereco_servico:
            endereco_base = self.endereco_servico
            if self.numero_servico:
                endereco_base += f", {self.numero_servico}"
            if self.complemento_servico:
                endereco_base += f", {self.complemento_servico}"
            partes.append(endereco_base)
        
        if self.bairro_servico:
            partes.append(self.bairro_servico)
        
        if self.cidade_servico and self.estado_servico:
            partes.append(f"{self.cidade_servico}/{self.estado_servico}")
        
        if self.cep_servico:
            partes.append(f"CEP: {self.cep_servico}")
        
        return ", ".join(partes) if partes else "Endereço não informado"
    
    def get_cidade_estado_servico(self):
        """Retorna cidade e estado do local do serviço"""
        if self.usar_endereco_usuario:
            return f"{self.cliente.cidade}, {self.cliente.estado}"
        return f"{self.cidade_servico}, {self.estado_servico}"
    
    def get_coordenadas_servico(self):
        """Retorna tupla (lat, lon) do local do serviço"""
        if self.usar_endereco_usuario:
            return (self.cliente.lat, self.cliente.lon)
        return (self.lat_servico, self.lon_servico)
    
    def get_cep_servico(self):
        """Retorna CEP do local do serviço"""
        if self.usar_endereco_usuario:
            return self.cliente.cep
        return self.cep_servico
    
    def endereco_servico_preenchido(self):
        """Verifica se o endereço do serviço está preenchido"""
        if self.usar_endereco_usuario:
            return bool(self.cliente.cidade and self.cliente.estado)
        return bool(self.cidade_servico and self.estado_servico)

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
