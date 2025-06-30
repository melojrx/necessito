from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from users.models import User

class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer para mensagens do chat"""
    
    remetente = serializers.StringRelatedField(read_only=True)
    remetente_id = serializers.IntegerField(source='remetente.id', read_only=True)
    data_envio_formatted = serializers.CharField(source='data_envio', read_only=True)
    tem_anexo = serializers.SerializerMethodField()
    arquivo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'conteudo', 'remetente', 'remetente_id', 
            'data_envio', 'data_envio_formatted', 'lida', 
            'tem_anexo', 'arquivo_url', 'tipo_arquivo'
        ]
        read_only_fields = ['id', 'data_envio', 'lida']
    
    def get_tem_anexo(self, obj):
        """Verifica se a mensagem tem anexo"""
        return bool(obj.arquivo_anexo)
    
    def get_arquivo_url(self, obj):
        """Retorna URL do arquivo anexo"""
        if obj.arquivo_anexo:
            return obj.arquivo_anexo.url
        return None
    
    def to_representation(self, instance):
        """Customizar representação da data"""
        data = super().to_representation(instance)
        data['data_envio_formatted'] = instance.data_envio.strftime('%d/%m/%Y %H:%M')
        return data

class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer para sala de chat"""
    
    cliente = serializers.StringRelatedField(read_only=True)
    fornecedor = serializers.StringRelatedField(read_only=True)
    necessidade_titulo = serializers.CharField(source='necessidade.titulo', read_only=True)
    ultima_mensagem = ChatMessageSerializer(read_only=True)
    total_mensagens = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'cliente', 'fornecedor', 'necessidade_titulo',
            'criado_em', 'ativo', 'ultima_mensagem', 'total_mensagens'
        ]
        read_only_fields = ['id', 'criado_em'] 