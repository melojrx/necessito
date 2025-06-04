# chat/models.py

from django.db import models
from django.utils import timezone
from users.models import User
from ads.models import Necessidade
from budgets.models import Orcamento  # Ajuste o import conforme sua estrutura

class ChatRoom(models.Model):
    """
    Sala de chat entre cliente (anunciante) e fornecedor para uma necessidade específica
    """
    necessidade = models.ForeignKey(
        Necessidade, 
        on_delete=models.CASCADE, 
        related_name='chat_rooms',
        verbose_name='Necessidade'
    )
    cliente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='chat_rooms_as_cliente',
        verbose_name='Cliente'
    )
    fornecedor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='chat_rooms_as_fornecedor',
        verbose_name='Fornecedor'
    )
    orcamento = models.ForeignKey(
        Orcamento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Orçamento Relacionado'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['necessidade', 'cliente', 'fornecedor']
        verbose_name = 'Sala de Chat'
        verbose_name_plural = 'Salas de Chat'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Chat: {self.necessidade.titulo} - {self.fornecedor.get_full_name()}"
    
    @property
    def ultima_mensagem(self):
        """Retorna a última mensagem do chat"""
        return self.mensagens.order_by('-data_envio').first()
    
    @property
    def total_mensagens(self):
        """Retorna o total de mensagens do chat"""
        return self.mensagens.count()

class ChatMessage(models.Model):
    """
    Mensagens trocadas no chat
    """
    chat_room = models.ForeignKey(
        ChatRoom, 
        on_delete=models.CASCADE, 
        related_name='mensagens'
    )
    remetente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='Remetente'
    )
    conteudo = models.TextField(verbose_name='Conteúdo')
    data_envio = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
    editada = models.BooleanField(default=False)
    data_edicao = models.DateTimeField(null=True, blank=True)
    
    # Campos opcionais para anexos
    arquivo_anexo = models.FileField(
        upload_to='chat_anexos/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text='Anexar arquivo (máximo 5MB)'
    )
    tipo_arquivo = models.CharField(
        max_length=20, 
        blank=True,
        choices=[
            ('imagem', 'Imagem'),
            ('documento', 'Documento'),
            ('outros', 'Outros')
        ]
    )
    
    class Meta:
        ordering = ['data_envio']
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
    
    def __str__(self):
        return f"{self.remetente.get_full_name()}: {self.conteudo[:50]}..."
    
    def marcar_como_lida(self):
        """Marca a mensagem como lida"""
        if not self.lida:
            self.lida = True
            self.save(update_fields=['lida'])
    
    def save(self, *args, **kwargs):
        # Auto-detectar tipo de arquivo
        if self.arquivo_anexo:
            nome_arquivo = self.arquivo_anexo.name.lower()
            if any(ext in nome_arquivo for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                self.tipo_arquivo = 'imagem'
            elif any(ext in nome_arquivo for ext in ['.pdf', '.doc', '.docx', '.txt']):
                self.tipo_arquivo = 'documento'
            else:
                self.tipo_arquivo = 'outros'
        
        super().save(*args, **kwargs)