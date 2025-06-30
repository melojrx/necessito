# chat/consumers.py

import json
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer
import socketio

User = get_user_model()
logger = logging.getLogger(__name__)

# Referência ao servidor Socket.IO (configurado em asgi.py)

class ChatNamespace(socketio.AsyncNamespace):
    """
    Namespace para gerenciar conexões de chat em tempo real
    """
    
    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.user_rooms = {}  # Mapeia session_id -> user_id
        
    async def on_connect(self, sid, environ, auth):
        """Usuário conectou ao WebSocket"""
        try:
            # Extrair user da sessão/auth
            user = await self._get_user_from_environ(environ)
            if not user or user.is_anonymous:
                logger.warning(f"Conexão rejeitada - usuário não autenticado: {sid}")
                return False
            
            self.user_rooms[sid] = user.id
            logger.info(f"Usuário {user.email} conectado: {sid}")
            
            # Entrar nas salas de chat do usuário
            await self._join_user_chat_rooms(sid, user)
            
            # Entrar na sala pessoal do usuário para receber notificações
            await self.enter_room(sid, f"user_{user.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na conexão: {e}")
            return False
    
    async def on_disconnect(self, sid):
        """Usuário desconectou"""
        user_id = self.user_rooms.get(sid)
        if user_id:
            try:
                user = await User.objects.aget(id=user_id)
                logger.info(f"Usuário {user.email} desconectado: {sid}")
            except User.DoesNotExist:
                pass
            del self.user_rooms[sid]
    
    async def on_join_chat(self, sid, data):
        """Usuário entrou em uma sala de chat específica"""
        try:
            chat_id = data.get('chat_id')
            user_id = self.user_rooms.get(sid)
            
            if not user_id or not chat_id:
                return
            
            # Verificar permissões
            user = await User.objects.aget(id=user_id)
            chat_room = await ChatRoom.objects.select_related(
                'cliente', 'fornecedor'
            ).aget(id=chat_id, ativo=True)
            
            if user not in [chat_room.cliente, chat_room.fornecedor]:
                await self.emit('error', {
                    'message': 'Permissão negada para acessar este chat'
                }, room=sid)
                return
            
            # Entrar na sala
            room_name = f"chat_{chat_id}"
            await self.enter_room(sid, room_name)
            
            logger.info(f"Usuário {user.email} entrou no chat {chat_id}")
            
            # Notificar entrada na sala
            await self.emit('user_joined', {
                'user': user.get_full_name(),
                'timestamp': self._get_timestamp()
            }, room=room_name, skip_sid=sid)
            
        except Exception as e:
            logger.error(f"Erro ao entrar no chat: {e}")
            await self.emit('error', {
                'message': 'Erro interno do servidor'
            }, room=sid)
    
    async def on_leave_chat(self, sid, data):
        """Usuário saiu de uma sala de chat"""
        try:
            chat_id = data.get('chat_id')
            if not chat_id:
                return
                
            room_name = f"chat_{chat_id}"
            await self.leave_room(sid, room_name)
            
            user_id = self.user_rooms.get(sid)
            if user_id:
                user = await User.objects.aget(id=user_id)
                logger.info(f"Usuário {user.email} saiu do chat {chat_id}")
                
                # Notificar saída da sala
                await self.emit('user_left', {
                    'user': user.get_full_name(),
                    'timestamp': self._get_timestamp()
                }, room=room_name)
                
        except Exception as e:
            logger.error(f"Erro ao sair do chat: {e}")
    
    async def on_send_message(self, sid, data):
        """Enviar nova mensagem"""
        try:
            user_id = self.user_rooms.get(sid)
            if not user_id:
                return
            
            chat_id = data.get('chat_id')
            conteudo = data.get('conteudo', '').strip()
            
            if not chat_id or not conteudo:
                await self.emit('error', {
                    'message': 'Chat ID e conteúdo são obrigatórios'
                }, room=sid)
                return
            
            # Verificar permissões e criar mensagem
            user = await User.objects.aget(id=user_id)
            chat_room = await ChatRoom.objects.select_related(
                'cliente', 'fornecedor'
            ).aget(id=chat_id, ativo=True)
            
            if user not in [chat_room.cliente, chat_room.fornecedor]:
                await self.emit('error', {
                    'message': 'Permissão negada'
                }, room=sid)
                return
            
            # Criar mensagem
            mensagem = await ChatMessage.objects.acreate(
                chat_room=chat_room,
                remetente=user,
                conteudo=conteudo
            )
            
            # Serializar mensagem
            message_data = {
                'id': mensagem.id,
                'conteudo': mensagem.conteudo,
                'remetente': mensagem.remetente.get_full_name(),
                'remetente_id': mensagem.remetente.id,
                'data_envio': mensagem.data_envio.strftime('%d/%m/%Y %H:%M'),
                'timestamp': self._get_timestamp()
            }
            
            # Enviar para todos na sala
            room_name = f"chat_{chat_id}"
            await self.emit('new_message', message_data, room=room_name)
            
            # Enviar notificação de nova mensagem para usuários conectados
            destinatario = chat_room.fornecedor if user == chat_room.cliente else chat_room.cliente
            
            # Emitir para a sala pessoal do destinatário
            await self.emit('new_notification', {
                'type': 'chat_message',
                'from_user': user.get_full_name(),
                'chat_id': chat_id,
                'message_preview': conteudo[:50] + "..." if len(conteudo) > 50 else conteudo,
                'timestamp': self._get_timestamp()
            }, room=f"user_{destinatario.id}")
            
            # Log para debug
            logger.info(f"Notificação enviada para sala user_{destinatario.id} - {destinatario.email}")
            
            logger.info(f"Nova mensagem enviada no chat {chat_id} por {user.email}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            await self.emit('error', {
                'message': 'Erro ao enviar mensagem'
            }, room=sid)
    
    async def on_typing_start(self, sid, data):
        """Usuário começou a digitar"""
        try:
            user_id = self.user_rooms.get(sid)
            chat_id = data.get('chat_id')
            
            if not user_id or not chat_id:
                return
            
            user = await User.objects.aget(id=user_id)
            room_name = f"chat_{chat_id}"
            
            await self.emit('user_typing', {
                'user': user.get_full_name(),
                'user_id': user.id,
                'is_typing': True
            }, room=room_name, skip_sid=sid)
            
        except Exception as e:
            logger.error(f"Erro no typing_start: {e}")
    
    async def on_typing_stop(self, sid, data):
        """Usuário parou de digitar"""
        try:
            user_id = self.user_rooms.get(sid)
            chat_id = data.get('chat_id')
            
            if not user_id or not chat_id:
                return
            
            user = await User.objects.aget(id=user_id)
            room_name = f"chat_{chat_id}"
            
            await self.emit('user_typing', {
                'user': user.get_full_name(),
                'user_id': user.id,
                'is_typing': False
            }, room=room_name, skip_sid=sid)
            
        except Exception as e:
            logger.error(f"Erro no typing_stop: {e}")
    
    async def on_join_user_room(self, sid, data):
        """Usuário entra na sala pessoal para receber notificações"""
        try:
            user_id = self.user_rooms.get(sid)
            if not user_id:
                return
            
            # Entrar na sala pessoal
            user_room = f"user_{user_id}"
            await self.enter_room(sid, user_room)
            
            logger.info(f"Usuário {user_id} entrou na sala de notificações: {user_room}")
            
            # Confirmar entrada na sala
            await self.emit('notification_room_joined', {
                'room': user_room,
                'timestamp': self._get_timestamp()
            }, room=sid)
            
        except Exception as e:
            logger.error(f"Erro ao entrar na sala de notificações: {e}")
    
    async def _get_user_from_environ(self, environ):
        """Extrair usuário autenticado do environ"""
        try:
            # Método simplificado - obtém user_id da query string
            query_string = environ.get('QUERY_STRING', '')
            if 'user_id=' in query_string:
                import re
                match = re.search(r'user_id=(\d+)', query_string)
                if match:
                    user_id = int(match.group(1))
                    user = await User.objects.aget(id=user_id)
                    return user
            
            # Fallback: tentar cookies de sessão
            from .auth import get_user_from_socket_session
            user = get_user_from_socket_session(environ)
            return user
            
        except Exception as e:
            logger.error(f"Erro ao obter usuário do environ: {e}")
            return None
    
    async def _join_user_chat_rooms(self, sid, user):
        """Entrar automaticamente nos chats do usuário"""
        try:
            # Buscar chats ativos do usuário
            chats = ChatRoom.objects.filter(
                Q(cliente=user) | Q(fornecedor=user),
                ativo=True
            )
            
            async for chat in chats:
                room_name = f"chat_{chat.id}"
                await self.enter_room(sid, room_name)
                
        except Exception as e:
            logger.error(f"Erro ao entrar nas salas do usuário: {e}")
    
    def _get_timestamp(self):
        """Retorna timestamp atual"""
        from django.utils import timezone
        return timezone.now().isoformat() 