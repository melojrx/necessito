from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User
from categories.models import Categoria, SubCategoria
from decimal import Decimal
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

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
        ('em_atendimento', 'Em atendimento'), # Anúncio com orçamento aceito pelo anunciante e pelo fornecedor. 
        ('finalizado', 'Finalizado'), # Após a entrega do serviço ou produto, o anúncio é finalizado manualmente pelo anunciante.
        ('cancelado', 'Cancelado'), # Anúncio cancelado pelo anunciante.
        ('expirado', 'Expirado'), # O anúncio atingiu sua data de validade sem fechar negócio
        ('em_disputa', 'Em disputa'), # Cliente ou fornecedor sinalizou um problema durante o atendimento
    ], default='ativo')
    ip_usuario = models.GenericIPAddressField(blank=True, null=True, help_text="Endereço IP do usuário que cadastrou o anúncio")
    duracao = models.CharField(max_length=20, blank=True, null=True, help_text="Duração do serviço ou entrega (ex.: 7 dias, 3 horas)")
    data_validade = models.DateTimeField(
        "Data de validade",
        null=True,
        blank=True,
        help_text="Data e hora em que o anúncio expirará automaticamente. Se não informado, será definido automaticamente para 30 dias após a criação."
    )
    
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
    
    # ==================== CAMPOS DE TIMESTAMPS PARA STATE MACHINE ====================
    data_primeiro_orcamento = models.DateTimeField(
        "Data do primeiro orçamento", 
        null=True, 
        blank=True,
        help_text="Timestamp de quando o primeiro orçamento foi recebido"
    )
    aguardando_confirmacao_desde = models.DateTimeField(
        "Aguardando confirmação desde", 
        null=True, 
        blank=True,
        help_text="Timestamp de quando entrou no status aguardando_confirmacao (timeout de 48h)"
    )
    data_finalizacao = models.DateTimeField(
        "Data de finalização", 
        null=True, 
        blank=True,
        help_text="Timestamp de quando a necessidade foi finalizada"
    )
    avaliacao_liberada = models.BooleanField(
        "Avaliação liberada",
        default=False,
        help_text="Se verdadeiro, permite avaliação entre cliente e fornecedor"
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
    
    def get_latitude_mapa(self):
        """Retorna a latitude para exibição no mapa"""
        if self.usar_endereco_usuario:
            return self.cliente.lat if self.cliente.lat else None
        return self.lat_servico
    
    def get_longitude_mapa(self):
        """Retorna a longitude para exibição no mapa"""
        if self.usar_endereco_usuario:
            return self.cliente.lon if self.cliente.lon else None
        return self.lon_servico
    
    def get_cidade_mapa(self):
        """Retorna a cidade para exibição no mapa"""
        if self.usar_endereco_usuario:
            return self.cliente.cidade
        return self.cidade_servico
    
    def get_estado_mapa(self):
        """Retorna o estado para exibição no mapa"""
        if self.usar_endereco_usuario:
            return self.cliente.estado
        return self.estado_servico
    
    def get_bairro_mapa(self):
        """Retorna o bairro para exibição no mapa"""
        if self.usar_endereco_usuario:
            return getattr(self.cliente, 'bairro', '')
        return self.bairro_servico
    
    def tem_coordenadas_mapa(self):
        """Verifica se tem coordenadas válidas para exibir o mapa"""
        lat = self.get_latitude_mapa()
        lon = self.get_longitude_mapa()
        return lat is not None and lon is not None
    
    # ==================== MÉTODOS DO STATE MACHINE ====================
    
    def get_state_machine(self):
        """Retorna uma instância do state machine para esta necessidade."""
        from core.state_machine import get_necessidade_state_machine
        return get_necessidade_state_machine(self)
    
    def can_transition_to(self, new_status, user=None, **kwargs):
        """Verifica se pode fazer transição para o novo status."""
        state_machine = self.get_state_machine()
        return state_machine.can_transition(new_status, user=user, **kwargs)
    
    def transition_to(self, new_status, user=None, **kwargs):
        """Executa transição de status usando o state machine."""
        state_machine = self.get_state_machine()
        return state_machine.transition_to(new_status, user=user, **kwargs)
    
    def get_valid_transitions(self):
        """Retorna lista de transições válidas a partir do status atual."""
        state_machine = self.get_state_machine()
        return state_machine.get_valid_transitions()
    
    def is_confirmation_expired(self):
        """Verifica se o timeout de confirmação expirou."""
        state_machine = self.get_state_machine()
        return state_machine.is_confirmation_expired()
    
    def handle_timeout(self):
        """Manipula timeout de confirmação automaticamente."""
        state_machine = self.get_state_machine()
        return state_machine.handle_timeout()
    
    def can_be_edited(self, user=None):
        """Verifica se a necessidade pode ser editada baseado no status."""
        if self.status in ['analisando_orcamentos', 'aguardando_confirmacao', 'em_atendimento', 'finalizado', 'cancelado']:
            return False
        return True
    
    def can_be_finalized(self, user=None):
        """Verifica se a necessidade pode ser finalizada."""
        if user and user != self.cliente:
            return False
        return self.status == 'em_atendimento'
    
    def can_be_cancelled(self, user=None):
        """Verifica se a necessidade pode ser cancelada."""
        if user and user != self.cliente:
            return False
        return self.status not in ['finalizado', 'cancelado']
    
    def get_accepted_budget(self):
        """Retorna o orçamento aceito (se houver)."""
        return self.orcamentos.filter(status='aceito_pelo_cliente').first()
    
    def get_confirmed_budget(self):
        """Retorna o orçamento confirmado (se houver)."""
        return self.orcamentos.filter(status='confirmado').first()
    
    # ==================== MÉTODOS DE DATA DE VALIDADE ====================
    
    def clean(self):
        """Validação customizada do modelo."""
        super().clean()
        # Pular validação se for uma operação de expiração automática
        if hasattr(self, '_skip_validation'):
            return
            
        if self.data_validade and self.data_validade <= timezone.now():
            raise ValidationError({
                'data_validade': 'A data de validade deve ser no futuro.'
            })
    
    def save(self, *args, **kwargs):
        """Override do save para definir data_validade automaticamente se não informada."""
        # Se é uma nova instância e não tem data_validade definida, define para 30 dias
        if not self.pk and not self.data_validade:
            self.data_validade = timezone.now() + timedelta(days=30)
        
        # Chama validação antes de salvar (apenas se não for para pular)
        if not kwargs.pop('skip_validation', False):
            self.clean()
        super().save(*args, **kwargs)
    
    def dias_restantes(self):
        """Calcula quantos dias restam até a expiração."""
        if not self.data_validade:
            return None
        
        diferenca = self.data_validade - timezone.now()
        if diferenca.total_seconds() <= 0:
            return 0
        
        return diferenca.days
    
    def horas_restantes(self):
        """Calcula quantas horas restam até a expiração."""
        if not self.data_validade:
            return None
        
        diferenca = self.data_validade - timezone.now()
        if diferenca.total_seconds() <= 0:
            return 0
        
        return int(diferenca.total_seconds() / 3600)
    
    def esta_expirado(self):
        """Verifica se o anúncio está expirado."""
        if not self.data_validade:
            return False
        return timezone.now() > self.data_validade
    
    def esta_proximo_da_expiracao(self, dias=3):
        """Verifica se o anúncio está próximo da expiração (padrão: 3 dias)."""
        if not self.data_validade:
            return False
        diferenca = self.data_validade - timezone.now()
        return 0 < diferenca.total_seconds() <= (dias * 24 * 3600)
    
    def tempo_restante_formatado(self):
        """Retorna o tempo restante formatado de forma legível."""
        if not self.data_validade:
            return "Sem prazo definido"
        
        if self.esta_expirado():
            return "Expirado"
        
        dias = self.dias_restantes()
        horas = self.horas_restantes() % 24
        
        if dias > 0:
            if dias == 1:
                return f"{dias} dia restante"
            return f"{dias} dias restantes"
        elif horas > 0:
            if horas == 1:
                return f"{horas} hora restante"
            return f"{horas} horas restantes"
        else:
            return "Expira em breve"

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


class Disputa(models.Model):
    """
    Model para sistema de disputas entre clientes e fornecedores.
    Permite mediação de conflitos durante o atendimento de necessidades.
    """
    
    # Relacionamentos principais
    necessidade = models.ForeignKey(
        Necessidade, 
        on_delete=models.CASCADE, 
        related_name='disputas',
        verbose_name='Necessidade em disputa'
    )
    orcamento = models.ForeignKey(
        'budgets.Orcamento', 
        on_delete=models.CASCADE, 
        related_name='disputas',
        verbose_name='Orçamento relacionado',
        help_text='Orçamento que estava sendo executado quando a disputa foi aberta'
    )
    
    # Usuário que iniciou a disputa
    usuario_abertura = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='disputas_abertas',
        verbose_name='Usuário que abriu a disputa'
    )
    
    # Detalhes da disputa
    motivo = models.TextField(
        'Motivo da disputa',
        help_text='Descreva detalhadamente o problema ou conflito'
    )
    
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('em_analise', 'Em análise'),
        ('resolvida', 'Resolvida'),
        ('cancelada', 'Cancelada'),
    ]
    status = models.CharField(
        'Status da disputa',
        max_length=20,
        choices=STATUS_CHOICES,
        default='aberta'
    )
    
    # Resolução da disputa (preenchido pelo admin)
    resolucao = models.TextField(
        'Resolução da disputa',
        blank=True,
        help_text='Resolução ou comentários do administrador'
    )
    
    # Usuário admin que resolveu a disputa
    resolvida_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputas_resolvidas',
        verbose_name='Resolvida por',
        help_text='Administrador que resolveu a disputa'
    )
    
    # Status final da necessidade após resolução
    STATUS_FINAL_CHOICES = [
        ('em_atendimento', 'Voltar para Em Atendimento'),
        ('finalizado', 'Finalizar Necessidade'),
        ('cancelado', 'Cancelar Necessidade'),
    ]
    status_final_necessidade = models.CharField(
        'Status final da necessidade',
        max_length=20,
        choices=STATUS_FINAL_CHOICES,
        blank=True,
        help_text='Para onde a necessidade deve ir após resolução da disputa'
    )
    
    # Anexos/evidências
    arquivo_evidencia = models.FileField(
        'Arquivo de evidência',
        upload_to='disputas/evidencias/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text='Anexe arquivos que comprovem sua alegação (fotos, documentos, etc.)'
    )
    
    # Timestamps
    data_abertura = models.DateTimeField('Data de abertura', auto_now_add=True)
    data_resolucao = models.DateTimeField('Data de resolução', null=True, blank=True)
    data_modificacao = models.DateTimeField('Última modificação', auto_now=True)
    
    # Metadados para auditoria
    ip_usuario_abertura = models.GenericIPAddressField(
        'IP do usuário',
        blank=True, 
        null=True,
        help_text="IP do usuário que abriu a disputa"
    )
    
    # Comentários internos (visível apenas para admins)
    comentarios_internos = models.TextField(
        'Comentários internos',
        blank=True,
        help_text='Comentários visíveis apenas para administradores'
    )
    
    class Meta:
        verbose_name = 'Disputa'
        verbose_name_plural = 'Disputas'
        ordering = ['-data_abertura']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['data_abertura']),
            models.Index(fields=['necessidade', 'status']),
            models.Index(fields=['usuario_abertura']),
        ]
    
    def __str__(self):
        return f"Disputa #{self.pk} - {self.necessidade.titulo}"
    
    def clean(self):
        """Validações customizadas do modelo."""
        super().clean()
        
        # Validar se a necessidade está em status válido para disputa
        if self.necessidade.status != 'em_atendimento':
            raise ValidationError({
                'necessidade': 'Disputas só podem ser abertas para necessidades em atendimento.'
            })
        
        # Validar se o orçamento está relacionado à necessidade
        if self.orcamento.anuncio != self.necessidade:
            raise ValidationError({
                'orcamento': 'O orçamento deve estar relacionado à necessidade em disputa.'
            })
        
        # Validar se o orçamento está confirmado
        if self.orcamento.status != 'confirmado':
            raise ValidationError({
                'orcamento': 'Só é possível abrir disputa para orçamentos confirmados.'
            })
        
        # Validar se o usuário pode abrir disputa (cliente ou fornecedor)
        if self.usuario_abertura not in [self.necessidade.cliente, self.orcamento.fornecedor]:
            raise ValidationError({
                'usuario_abertura': 'Apenas cliente ou fornecedor podem abrir disputas.'
            })
    
    def save(self, *args, **kwargs):
        """Override do save para controlar transições de estado."""
        is_new = not self.pk
        old_status = None
        
        if not is_new:
            old_instance = Disputa.objects.get(pk=self.pk)
            old_status = old_instance.status
        
        # Definir data de resolução quando status muda para resolvida
        if self.status == 'resolvida' and old_status != 'resolvida':
            if not self.data_resolucao:
                from django.utils import timezone
                self.data_resolucao = timezone.now()
        
        # Chama validação antes de salvar
        self.clean()
        super().save(*args, **kwargs)
        
        # Se é nova disputa, atualizar status da necessidade
        if is_new:
            self._atualizar_status_necessidade_para_disputa()
        
        # Se disputa foi resolvida, executar ações pós-resolução
        if self.status == 'resolvida' and old_status != 'resolvida':
            self._executar_pos_resolucao()
    
    def _atualizar_status_necessidade_para_disputa(self):
        """Atualiza status da necessidade para 'em_disputa' quando disputa é aberta."""
        try:
            state_machine = self.necessidade.get_state_machine()
            state_machine.transition_to('em_disputa')
            logger.info(f"Necessidade {self.necessidade.pk} movida para 'em_disputa' devido à disputa {self.pk}")
        except Exception as e:
            logger.error(f"Erro ao atualizar status da necessidade para disputa: {e}")
    
    def _executar_pos_resolucao(self):
        """Executa ações após resolução da disputa."""
        if not self.status_final_necessidade:
            logger.warning(f"Disputa {self.pk} resolvida sem status final definido")
            return
        
        try:
            state_machine = self.necessidade.get_state_machine()
            state_machine.transition_to(self.status_final_necessidade, user=self.resolvida_por)
            
            # Enviar notificações
            self._enviar_notificacoes_resolucao()
            
            logger.info(f"Disputa {self.pk} resolvida. Necessidade movida para '{self.status_final_necessidade}'")
        except Exception as e:
            logger.error(f"Erro ao executar pós-resolução da disputa {self.pk}: {e}")
    
    def _enviar_notificacoes_resolucao(self):
        """Envia notificações quando disputa é resolvida."""
        try:
            from notifications.models import Notification, NotificationType
            
            # Notificar cliente
            Notification.objects.create(
                user=self.necessidade.cliente,
                title='Disputa Resolvida',
                message=f'A disputa sobre "{self.necessidade.titulo}" foi resolvida pela administração.',
                notification_type=NotificationType.SYSTEM_MESSAGE,
                necessidade=self.necessidade,
                metadata={'disputa_id': self.pk, 'resolucao': self.resolucao}
            )
            
            # Notificar fornecedor
            Notification.objects.create(
                user=self.orcamento.fornecedor,
                title='Disputa Resolvida',
                message=f'A disputa sobre "{self.necessidade.titulo}" foi resolvida pela administração.',
                notification_type=NotificationType.SYSTEM_MESSAGE,
                necessidade=self.necessidade,
                metadata={'disputa_id': self.pk, 'resolucao': self.resolucao}
            )
            
        except ImportError:
            logger.warning("Sistema de notificações não disponível")
    
    # Métodos de permissão e estado
    def pode_ser_resolvida_por(self, user):
        """Verifica se usuário pode resolver a disputa."""
        return user.is_staff or user.is_superuser
    
    def pode_ser_cancelada_por(self, user):
        """Verifica se usuário pode cancelar a disputa."""
        # Apenas quem abriu pode cancelar (se ainda estiver aberta)
        return (self.usuario_abertura == user and self.status == 'aberta') or user.is_staff
    
    def pode_ser_visualizada_por(self, user):
        """Verifica se usuário pode visualizar a disputa."""
        return (
            user == self.necessidade.cliente or 
            user == self.orcamento.fornecedor or 
            user.is_staff
        )
    
    def get_contraparte(self, user):
        """Retorna a contraparte na disputa (cliente ou fornecedor)."""
        if user == self.necessidade.cliente:
            return self.orcamento.fornecedor
        elif user == self.orcamento.fornecedor:
            return self.necessidade.cliente
        return None
    
    def get_tipo_usuario_abertura(self):
        """Retorna se quem abriu foi cliente ou fornecedor."""
        if self.usuario_abertura == self.necessidade.cliente:
            return 'cliente'
        elif self.usuario_abertura == self.orcamento.fornecedor:
            return 'fornecedor'
        return 'outro'
    
    def get_dias_em_aberto(self):
        """Retorna quantos dias a disputa está em aberto."""
        from django.utils import timezone
        if self.status in ['resolvida', 'cancelada']:
            data_fim = self.data_resolucao or self.data_modificacao
        else:
            data_fim = timezone.now()
        
        diferenca = data_fim - self.data_abertura
        return diferenca.days
    
    def get_absolute_url(self):
        """Retorna URL absoluta da disputa."""
        from django.urls import reverse
        return reverse('ads:disputa_detail', args=[str(self.pk)])
    
    @property
    def esta_ativa(self):
        """Verifica se a disputa está ativa (não resolvida nem cancelada)."""
        return self.status in ['aberta', 'em_analise']
    
    @property
    def precisa_atencao_admin(self):
        """Verifica se a disputa precisa de atenção administrativa."""
        if self.status != 'aberta':
            return False
        
        # Disputas abertas há mais de 48 horas precisam de atenção
        from django.utils import timezone
        return (timezone.now() - self.data_abertura).total_seconds() > 48 * 3600
