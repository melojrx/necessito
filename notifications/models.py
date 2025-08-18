from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ads.models import Necessidade
from core import settings

class NotificationType(models.TextChoices):
    # Necessidade lifecycle
    NEW_AD = 'NEW_AD', 'Nova Necessidade Criada'
    NEW_END_AD = 'NEW_END_AD', 'Necessidade Finalizada'
    AD_CANCELLED = 'AD_CANCELLED', 'Necessidade Cancelada'
    NECESSIDADE_EXPIRADA = 'NECESSIDADE_EXPIRADA', 'Necessidade Expirada'
    
    # Orçamento lifecycle
    NEW_BUDGET = 'NEW_BUDGET', 'Novo Orçamento Recebido'
    NOVO_ORCAMENTO = 'NOVO_ORCAMENTO', 'Orçamento Enviado'
    BUDGET_ACCEPTED = 'BUDGET_ACCEPTED', 'Orçamento Aceito pelo Cliente'
    ORCAMENTO_ACEITO = 'ORCAMENTO_ACEITO', 'Seu Orçamento foi Aceito'
    BUDGET_CONFIRMED = 'BUDGET_CONFIRMED', 'Orçamento Confirmado pelo Fornecedor'
    ORCAMENTO_CONFIRMADO = 'ORCAMENTO_CONFIRMADO', 'Orçamento Confirmado'
    BUDGET_REFUSED = 'BUDGET_REFUSED', 'Orçamento Recusado'
    ORCAMENTO_REJEITADO = 'ORCAMENTO_REJEITADO', 'Orçamento Rejeitado'
    ORCAMENTO_RECUSADO = 'ORCAMENTO_RECUSADO', 'Orçamento Recusado pelo Fornecedor'
    
    # Service lifecycle
    SERVICE_STARTED = 'SERVICE_STARTED', 'Serviço Iniciado'
    SERVICE_COMPLETED = 'SERVICE_COMPLETED', 'Serviço Finalizado'
    AVALIACAO_LIBERADA = 'AVALIACAO_LIBERADA', 'Avaliação Liberada'
    
    # Warnings and timeouts
    TIMEOUT_WARNING = 'TIMEOUT_WARNING', 'Aviso de Timeout'
    CONFIRMATION_TIMEOUT = 'CONFIRMATION_TIMEOUT', 'Timeout de Confirmação'
    
    # Chat and messaging
    NEW_CHAT_MESSAGE = 'NEW_CHAT_MESSAGE', 'Nova Mensagem no Chat'
    
    # Dispute notifications
    DISPUTE_OPENED = 'DISPUTE_OPENED', 'Nova Disputa Aberta'
    DISPUTE_RESOLVED = 'DISPUTE_RESOLVED', 'Disputa Resolvida'
    DISPUTE_ADMIN_ALERT = 'DISPUTE_ADMIN_ALERT', 'Nova Disputa para Análise'
    
    # System notifications
    SYSTEM_MESSAGE = 'SYSTEM_MESSAGE', 'Mensagem do Sistema'
    WELCOME = 'WELCOME', 'Bem-vindo'
    ACCOUNT_VERIFIED = 'ACCOUNT_VERIFIED', 'Conta Verificada'


class NotificationPriority(models.TextChoices):
    LOW = 'low', 'Baixa'
    NORMAL = 'normal', 'Normal'
    HIGH = 'high', 'Alta'
    URGENT = 'urgent', 'Urgente'


class DeliveryMethod(models.TextChoices):
    IN_APP = 'in_app', 'No Aplicativo'
    EMAIL = 'email', 'E-mail'
    SMS = 'sms', 'SMS'
    PUSH = 'push', 'Push Notification'

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name='Usuário'
    )
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensagem')
    notification_type = models.CharField(
        'Tipo de Notificação',
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM_MESSAGE
    )
    priority = models.CharField(
        'Prioridade',
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL
    )
    
    # Related objects
    necessidade = models.ForeignKey(
        'ads.Necessidade', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Necessidade'
    )
    orcamento = models.ForeignKey(
        'budgets.Orcamento', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Orçamento'
    )
    
    # Status and tracking
    is_read = models.BooleanField('Lida', default=False)
    read_at = models.DateTimeField('Lida em', null=True, blank=True)
    created_at = models.DateTimeField('Criada em', auto_now_add=True)
    
    # Delivery tracking
    email_sent = models.BooleanField('E-mail enviado', default=False)
    email_sent_at = models.DateTimeField('E-mail enviado em', null=True, blank=True)
    email_error = models.TextField('Erro no e-mail', blank=True)
    
    # Action tracking
    action_url = models.URLField('URL da ação', blank=True)
    action_taken = models.BooleanField('Ação realizada', default=False)
    action_taken_at = models.DateTimeField('Ação realizada em', null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField('Metadados', default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = models.timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_action_taken(self):
        """Mark that user took action on this notification."""
        if not self.action_taken:
            self.action_taken = True
            self.action_taken_at = models.timezone.now()
            self.save(update_fields=['action_taken', 'action_taken_at'])
    
    @property
    def is_urgent(self):
        """Check if notification is urgent."""
        return self.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]
    
    @property
    def age_in_hours(self):
        """Get age of notification in hours."""
        from django.utils import timezone
        delta = timezone.now() - self.created_at
        return delta.total_seconds() / 3600


class UserNotificationPreferences(models.Model):
    """User preferences for notifications."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='Usuário'
    )
    
    # General preferences
    enabled = models.BooleanField('Notificações habilitadas', default=True)
    
    # Delivery method preferences
    email_enabled = models.BooleanField('E-mail habilitado', default=True)
    in_app_enabled = models.BooleanField('Notificações no app habilitadas', default=True)
    sms_enabled = models.BooleanField('SMS habilitado', default=False)
    push_enabled = models.BooleanField('Push notifications habilitadas', default=True)
    
    # Frequency preferences
    instant_notifications = models.BooleanField('Notificações instantâneas', default=True)
    daily_digest = models.BooleanField('Resumo diário', default=False)
    weekly_digest = models.BooleanField('Resumo semanal', default=False)
    
    # Notification type preferences
    new_budget_notifications = models.BooleanField('Novos orçamentos', default=True)
    budget_status_notifications = models.BooleanField('Status de orçamentos', default=True)
    service_notifications = models.BooleanField('Notificações de serviço', default=True)
    chat_notifications = models.BooleanField('Mensagens de chat', default=True)
    dispute_notifications = models.BooleanField('Notificações de disputas', default=True)
    timeout_warnings = models.BooleanField('Avisos de timeout', default=True)
    system_notifications = models.BooleanField('Notificações do sistema', default=True)
    marketing_notifications = models.BooleanField('Notificações de marketing', default=False)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField('Horário silencioso habilitado', default=False)
    quiet_start_time = models.TimeField('Início do horário silencioso', null=True, blank=True)
    quiet_end_time = models.TimeField('Fim do horário silencioso', null=True, blank=True)
    
    # Timezone
    timezone = models.CharField(
        'Fuso horário',
        max_length=50,
        default='America/Sao_Paulo',
        help_text='Fuso horário para controle de horário silencioso'
    )
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Preferências de Notificação'
        verbose_name_plural = 'Preferências de Notificações'
    
    def __str__(self):
        return f"Preferências de {self.user.get_full_name()}"
    
    def should_send_email(self, notification_type=None):
        """Check if email should be sent for this notification type."""
        if not self.enabled or not self.email_enabled:
            return False
        
        # Check specific type preferences
        type_mapping = {
            NotificationType.NEW_BUDGET: self.new_budget_notifications,
            NotificationType.NOVO_ORCAMENTO: self.new_budget_notifications,
            NotificationType.BUDGET_ACCEPTED: self.budget_status_notifications,
            NotificationType.ORCAMENTO_ACEITO: self.budget_status_notifications,
            NotificationType.BUDGET_CONFIRMED: self.budget_status_notifications,
            NotificationType.ORCAMENTO_CONFIRMADO: self.budget_status_notifications,
            NotificationType.SERVICE_STARTED: self.service_notifications,
            NotificationType.SERVICE_COMPLETED: self.service_notifications,
            NotificationType.NEW_CHAT_MESSAGE: self.chat_notifications,
            NotificationType.DISPUTE_OPENED: self.dispute_notifications,
            NotificationType.DISPUTE_RESOLVED: self.dispute_notifications,
            NotificationType.DISPUTE_ADMIN_ALERT: self.system_notifications,
            NotificationType.TIMEOUT_WARNING: self.timeout_warnings,
            NotificationType.SYSTEM_MESSAGE: self.system_notifications,
        }
        
        if notification_type in type_mapping:
            return type_mapping[notification_type]
        
        return True
    
    def is_quiet_hours(self):
        """Check if current time is within quiet hours."""
        if not self.quiet_hours_enabled or not self.quiet_start_time or not self.quiet_end_time:
            return False
        
        from django.utils import timezone
        import pytz
        
        try:
            tz = pytz.timezone(self.timezone)
            now = timezone.now().astimezone(tz).time()
            
            if self.quiet_start_time <= self.quiet_end_time:
                return self.quiet_start_time <= now <= self.quiet_end_time
            else:
                # Spans midnight
                return now >= self.quiet_start_time or now <= self.quiet_end_time
        except:
            return False


class NotificationTemplate(models.Model):
    """Email templates for different notification types."""
    notification_type = models.CharField(
        'Tipo de Notificação',
        max_length=30,
        choices=NotificationType.choices,
        unique=True
    )
    
    subject = models.CharField('Assunto', max_length=200)
    html_content = models.TextField('Conteúdo HTML')
    text_content = models.TextField('Conteúdo Texto', blank=True)
    
    # Template variables documentation
    available_variables = models.TextField(
        'Variáveis Disponíveis',
        blank=True,
        help_text='Documentação das variáveis disponíveis no template'
    )
    
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Template de Notificação'
        verbose_name_plural = 'Templates de Notificação'
    
    def __str__(self):
        return f"Template: {self.get_notification_type_display()}"


class NotificationBatch(models.Model):
    """Batch processing for notifications."""
    name = models.CharField('Nome', max_length=200)
    notification_type = models.CharField(
        'Tipo de Notificação',
        max_length=30,
        choices=NotificationType.choices
    )
    
    # Targeting
    target_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Usuários alvo',
        blank=True
    )
    target_criteria = models.JSONField(
        'Critérios de alvo',
        default=dict,
        blank=True,
        help_text='Critérios para seleção automática de usuários'
    )
    
    # Content
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensagem')
    metadata = models.JSONField('Metadados', default=dict, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('scheduled', 'Agendado'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    ]
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Scheduling
    scheduled_for = models.DateTimeField('Agendado para', null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    sent_at = models.DateTimeField('Enviado em', null=True, blank=True)
    total_notifications = models.PositiveIntegerField('Total de notificações', default=0)
    successful_notifications = models.PositiveIntegerField('Notificações enviadas', default=0)
    failed_notifications = models.PositiveIntegerField('Notificações falharam', default=0)
    
    class Meta:
        verbose_name = 'Lote de Notificações'
        verbose_name_plural = 'Lotes de Notificações'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class NotificationLog(models.Model):
    """Log of all notification delivery attempts."""
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='delivery_logs',
        verbose_name='Notificação'
    )
    
    delivery_method = models.CharField(
        'Método de entrega',
        max_length=20,
        choices=DeliveryMethod.choices
    )
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregue'),
        ('failed', 'Falhou'),
        ('bounced', 'Rejeitado'),
    ]
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Delivery details
    attempted_at = models.DateTimeField('Tentativa em', auto_now_add=True)
    delivered_at = models.DateTimeField('Entregue em', null=True, blank=True)
    error_message = models.TextField('Mensagem de erro', blank=True)
    
    # External service details
    external_id = models.CharField('ID externo', max_length=200, blank=True)
    external_response = models.JSONField('Resposta externa', default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Log de Notificação'
        verbose_name_plural = 'Logs de Notificações'
        ordering = ['-attempted_at']
    
    def __str__(self):
        return f"{self.delivery_method} - {self.notification.title} ({self.get_status_display()})"

