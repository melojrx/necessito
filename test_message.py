#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chat.models import ChatMessage, ChatRoom
from users.models import User

print("=== TESTE CRIAÇÃO MENSAGEM ===")

# Buscar dados existentes
chat_room = ChatRoom.objects.first()
user = User.objects.get(email='jrmeloafrf@gmail.com')

print(f"ChatRoom: {chat_room}")
print(f"User: {user}")

# Teste 1: Criar mensagem diretamente
print("\n--- TESTE 1: Criar mensagem diretamente ---")
mensagem1 = ChatMessage.objects.create(
    chat_room=chat_room,
    remetente=user,
    conteudo="TESTE DIRETO 123"
)
print(f"Mensagem1 criada - ID: {mensagem1.id}, conteudo: '{mensagem1.conteudo}'")

# Verificar no banco
mensagem1_db = ChatMessage.objects.get(id=mensagem1.id)
print(f"Mensagem1 do DB - ID: {mensagem1_db.id}, conteudo: '{mensagem1_db.conteudo}'")

# Teste 2: Criar com save()
print("\n--- TESTE 2: Criar com save() ---")
mensagem2 = ChatMessage(
    chat_room=chat_room,
    remetente=user,
    conteudo="TESTE SAVE 456"
)
print(f"Antes do save - conteudo: '{mensagem2.conteudo}'")
mensagem2.save()
print(f"Após save - ID: {mensagem2.id}, conteudo: '{mensagem2.conteudo}'")

# Verificar no banco
mensagem2_db = ChatMessage.objects.get(id=mensagem2.id)
print(f"Mensagem2 do DB - ID: {mensagem2_db.id}, conteudo: '{mensagem2_db.conteudo}'") 