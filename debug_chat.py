#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chat.models import ChatMessage, ChatRoom
from users.models import User

print("=== DEBUG CHAT ===")

print(f"Total de ChatRooms: {ChatRoom.objects.count()}")
print(f"Total de ChatMessages: {ChatMessage.objects.count()}")

# Listar todas as mensagens
print("\n--- MENSAGENS ---")
for msg in ChatMessage.objects.all():
    print(f"ID: {msg.id}")
    print(f"Remetente: {msg.remetente.get_full_name()} ({msg.remetente.email})")
    print(f"Conteudo: '{msg.conteudo}'")
    print(f"Data: {msg.data_envio}")
    print(f"Chat Room ID: {msg.chat_room.id}")
    print("---")

# Verificar chat room específico
if ChatRoom.objects.exists():
    chat_room = ChatRoom.objects.first()
    print(f"\n--- CHAT ROOM {chat_room.id} ---")
    print(f"Necessidade: {chat_room.necessidade.titulo}")
    print(f"Cliente: {chat_room.cliente.get_full_name()}")
    print(f"Fornecedor: {chat_room.fornecedor.get_full_name()}")
    print(f"Mensagens neste chat: {chat_room.mensagens.count()}")
    
    for msg in chat_room.mensagens.all():
        print(f"  -> {msg.remetente.get_short_name()}: '{msg.conteudo}'") 