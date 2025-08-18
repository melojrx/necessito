# chat/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Max, Count, Prefetch
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
import json
import os
import logging

from .models import ChatRoom, ChatMessage
from ads.models import Necessidade
from budgets.models import Orcamento

@login_required
def lista_chats(request):
    """Lista todos os chats do usuário logado"""
    
    # Busca chats onde o usuário é cliente ou fornecedor
    chat_rooms = ChatRoom.objects.filter(
        Q(cliente=request.user) | Q(fornecedor=request.user),
        ativo=True
    ).select_related(
        'necessidade', 
        'cliente', 
        'fornecedor', 
        'orcamento'
    ).annotate(
        ultima_mensagem_data=Max('mensagens__data_envio'),
        mensagens_nao_lidas=Count(
            'mensagens', 
            filter=Q(mensagens__lida=False) & ~Q(mensagens__remetente=request.user)
        )
    ).order_by('-ultima_mensagem_data')
    
    # Paginação
    paginator = Paginator(chat_rooms, 15)
    page_number = request.GET.get('page')
    chats = paginator.get_page(page_number)
    
    # Contexto para o template
    context = {
        'chats': chats,
        'total_chats': chat_rooms.count(),
        'chats_nao_lidos': sum(chat.mensagens_nao_lidas for chat in chats)
    }
    
    return render(request, 'chat/lista_chats.html', context)

@login_required
def chat_detail(request, chat_id):
    """Exibe a interface de um chat específico"""
    
    chat_room = get_object_or_404(
        ChatRoom.objects.select_related(
            'necessidade', 
            'cliente', 
            'fornecedor', 
            'orcamento'
        ), 
        id=chat_id,
        ativo=True
    )
    
    # Verificar permissões
    if request.user not in [chat_room.cliente, chat_room.fornecedor]:
        messages.error(request, "Você não tem permissão para acessar este chat.")
        return redirect('chat:lista_chats')
    
    # Verificar se o chat ainda está disponível para novas mensagens
    chat_disponivel = chat_room.necessidade.status in ['em_atendimento', 'em_disputa']
    if not chat_disponivel:
        messages.warning(request, "Este chat está bloqueado. Novas mensagens só são permitidas quando o anúncio está 'Em Atendimento' ou 'Em Disputa'.")
    
    # Marcar mensagens como lidas
    ChatMessage.objects.filter(
        chat_room=chat_room,
        lida=False
    ).exclude(remetente=request.user).update(lida=True)
    
    # Buscar mensagens com paginação
    mensagens = chat_room.mensagens.select_related('remetente').order_by('data_envio')
    paginator = Paginator(mensagens, 50)
    page_number = request.GET.get('page')
    mensagens_paginadas = paginator.get_page(page_number)
    
    # Determinar papel do usuário
    is_cliente = request.user == chat_room.cliente
    
    context = {
        'chat_room': chat_room,
        'mensagens': mensagens_paginadas,
        'is_cliente': is_cliente,
        'outro_usuario': chat_room.fornecedor if is_cliente else chat_room.cliente,
    }
    
    return render(request, 'chat/chat_detail.html', context)

@login_required
def chat_websocket(request, chat_id):
    """Exibe a interface de chat com WebSocket (versão moderna)"""
    
    chat_room = get_object_or_404(
        ChatRoom.objects.select_related(
            'necessidade', 
            'cliente', 
            'fornecedor', 
            'orcamento'
        ), 
        id=chat_id,
        ativo=True
    )
    
    # Verificar permissões
    if request.user not in [chat_room.cliente, chat_room.fornecedor]:
        messages.error(request, "Você não tem permissão para acessar este chat.")
        return redirect('chat:lista_chats')
    
    # Marcar mensagens como lidas
    ChatMessage.objects.filter(
        chat_room=chat_room,
        lida=False
    ).exclude(remetente=request.user).update(lida=True)
    
    # Buscar mensagens com paginação
    mensagens = chat_room.mensagens.select_related('remetente').order_by('data_envio')
    paginator = Paginator(mensagens, 50)
    page_number = request.GET.get('page')
    mensagens_paginadas = paginator.get_page(page_number)
    
    # Verificar se o chat ainda está disponível para novas mensagens
    chat_disponivel = chat_room.necessidade.status in ['em_atendimento', 'em_disputa']
    if not chat_disponivel:
        messages.warning(request, "Este chat está bloqueado. Novas mensagens só são permitidas quando o anúncio está 'Em Atendimento' ou 'Em Disputa'.")
    
    # Determinar papel do usuário
    is_cliente = request.user == chat_room.cliente
    
    context = {
        'chat_room': chat_room,
        'mensagens': mensagens_paginadas,
        'is_cliente': is_cliente,
        'outro_usuario': chat_room.fornecedor if is_cliente else chat_room.cliente,
        'use_websocket': True,  # Flag para ativar WebSocket
        'chat_disponivel': chat_disponivel,
    }
    
    return render(request, 'chat/chat_detail.html', context)

@login_required
@require_http_methods(["POST"])
def enviar_mensagem(request, chat_id):
    """API para enviar nova mensagem"""
    
    logger = logging.getLogger(__name__)
    
    chat_room = get_object_or_404(ChatRoom, id=chat_id, ativo=True)
    
    # Verificar permissões
    if request.user not in [chat_room.cliente, chat_room.fornecedor]:
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    # Verificar se a necessidade ainda está em atendimento ou disputa
    if chat_room.necessidade.status not in ['em_atendimento', 'em_disputa']:
        return JsonResponse({
            'error': 'Chat não disponível. O anúncio precisa estar "Em Atendimento" ou "Em Disputa".'
        }, status=403)
    
    try:
        logger.info(f"=== DEBUG ENVIAR MENSAGEM ===")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"POST data: {request.POST}")
        logger.info(f"FILES: {request.FILES}")
        
        # Processar dados da requisição
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            conteudo = data.get('conteudo', '').strip()
            arquivo = None
            logger.info(f"JSON mode - conteudo: '{conteudo}'")
        else:
            # Form data com possível arquivo
            conteudo = request.POST.get('conteudo', '').strip()
            arquivo = request.FILES.get('arquivo_anexo')
            logger.info(f"Form mode - conteudo: '{conteudo}', arquivo: {arquivo}")
        
        logger.info(f"Conteudo final: '{conteudo}' (length: {len(conteudo)})")
        logger.info(f"Arquivo final: {arquivo}")
        
        # Validações
        if not conteudo and not arquivo:
            logger.warning("Conteudo e arquivo vazios!")
            return JsonResponse({'error': 'Mensagem ou arquivo é obrigatório'}, status=400)
        
        if conteudo and len(conteudo) > 2000:
            return JsonResponse({'error': 'Mensagem muito longa (máximo 2000 caracteres)'}, status=400)
        
        # Validar arquivo se presente
        if arquivo:
            if arquivo.size > 5 * 1024 * 1024:  # 5MB
                return JsonResponse({'error': 'Arquivo muito grande (máximo 5MB)'}, status=400)
        
        # Criar mensagem
        logger.info(f"Prestes a criar mensagem com conteudo: '{conteudo}'")
        
        # Corrigir lógica do conteúdo
        if conteudo:
            conteudo_final = conteudo
        elif arquivo:
            conteudo_final = f"[Arquivo: {arquivo.name}]"
        else:
            conteudo_final = ""
            
        logger.info(f"Conteudo final calculado: '{conteudo_final}'")
        
        mensagem = ChatMessage.objects.create(
            chat_room=chat_room,
            remetente=request.user,
            conteudo=conteudo_final,
            arquivo_anexo=arquivo
        )
        
        logger.info(f"Mensagem criada - ID: {mensagem.id}, conteudo: '{mensagem.conteudo}'")
        
        # Verificar no banco de dados
        mensagem_db = ChatMessage.objects.get(id=mensagem.id)
        logger.info(f"Mensagem lida do DB - ID: {mensagem_db.id}, conteudo: '{mensagem_db.conteudo}'")
        
        # Retornar dados da mensagem
        response_data = {
            'success': True,
            'mensagem': {
                'id': mensagem.id,
                'conteudo': mensagem.conteudo,
                'remetente': mensagem.remetente.get_full_name(),
                'data_envio': mensagem.data_envio.strftime('%d/%m/%Y %H:%M'),
                'is_own_message': True,
                'tem_anexo': bool(mensagem.arquivo_anexo),
                'arquivo_url': mensagem.arquivo_anexo.url if mensagem.arquivo_anexo else None,
                'tipo_arquivo': mensagem.tipo_arquivo
            }
        }
        
        logger.info(f"Resposta enviada: {response_data}")
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    except Exception as e:
        logger.error(f"Erro interno: {str(e)}")
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)

@login_required
def iniciar_chat(request, necessidade_id):
    """Inicia um chat entre fornecedor e cliente"""
    
    # Chat permitido apenas em status 'em_atendimento' ou 'em_disputa' conforme regras de negócio
    try:
        necessidade = get_object_or_404(
            Necessidade, 
            id=necessidade_id
        )
        
        if necessidade.status not in ['em_atendimento', 'em_disputa']:
            messages.error(request, f"Chat não disponível. O anúncio precisa estar 'Em Atendimento' ou 'Em Disputa' para habilitar o chat.")
            return redirect('ads:necessidade_detail', pk=necessidade_id)
            
    except:
        messages.error(request, f"Anúncio não encontrado.")
        return redirect('ads:necessidade_detail', pk=necessidade_id)
    
    # Verificar se não é o próprio cliente
    if request.user == necessidade.cliente:
        messages.error(request, "Você não pode iniciar um chat com sua própria necessidade.")
        return redirect('ads:necessidade_detail', pk=necessidade.id)
    
    # Verificar se o fornecedor tem orçamento para esta necessidade
    orcamento = Orcamento.objects.filter(
        anuncio=necessidade,
        fornecedor=request.user
    ).first()
    
    if not orcamento:
        messages.error(request, f"Você precisa enviar um orçamento antes de iniciar o chat. (Usuário: {request.user.email})")
        return redirect('ads:necessidade_detail', pk=necessidade.id)
    
    # Buscar ou criar chat room
    chat_room, created = ChatRoom.objects.get_or_create(
        necessidade=necessidade,
        cliente=necessidade.cliente,
        fornecedor=request.user,
        defaults={
            'orcamento': orcamento,
            'ativo': True
        }
    )
    
    if created:
        # Mensagem automática de boas-vindas
        ChatMessage.objects.create(
            chat_room=chat_room,
            remetente=request.user,
            conteudo=f"Olá! Estou interessado em conversar sobre '{necessidade.titulo}'. Enviei um orçamento de R$ {orcamento.valor_total():,.2f}."
        )
        messages.success(request, "Chat iniciado com sucesso!")
    else:
        messages.info(request, "Continuando conversa existente.")
    
    return redirect('chat:chat_detail', chat_id=chat_room.id)

@login_required
def buscar_mensagens_novas(request, chat_id):
    """API para buscar novas mensagens (polling)"""
    
    import logging
    logger = logging.getLogger(__name__)
    
    chat_room = get_object_or_404(ChatRoom, id=chat_id, ativo=True)
    
    # Verificar permissões
    if request.user not in [chat_room.cliente, chat_room.fornecedor]:
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    ultima_mensagem_id = int(request.GET.get('ultima_mensagem_id', 0))
    
    logger.info(f"=== DEBUG BUSCAR MENSAGENS NOVAS ===")
    logger.info(f"Usuario atual: {request.user.email}")
    logger.info(f"Ultima mensagem ID: {ultima_mensagem_id}")
    
    # Buscar mensagens mais recentes
    mensagens_novas = ChatMessage.objects.filter(
        chat_room=chat_room,
        id__gt=ultima_mensagem_id
    ).select_related('remetente').order_by('data_envio')
    
    logger.info(f"Encontradas {mensagens_novas.count()} mensagens novas")
    
    # Marcar como lidas (exceto as próprias)
    mensagens_novas.exclude(remetente=request.user).update(lida=True)
    
    # Serializar mensagens
    mensagens_data = []
    for mensagem in mensagens_novas:
        is_own = mensagem.remetente == request.user
        logger.info(f"Mensagem ID {mensagem.id}: remetente={mensagem.remetente.email}, is_own={is_own}")
        
        mensagens_data.append({
            'id': mensagem.id,
            'conteudo': mensagem.conteudo,
            'remetente': mensagem.remetente.get_full_name(),
            'data_envio': mensagem.data_envio.strftime('%d/%m/%Y %H:%M'),
            'is_own_message': is_own,
            'tem_anexo': bool(mensagem.arquivo_anexo),
            'arquivo_url': mensagem.arquivo_anexo.url if mensagem.arquivo_anexo else None,
            'tipo_arquivo': mensagem.tipo_arquivo
        })
    
    logger.info(f"Dados retornados: {mensagens_data}")
    
    return JsonResponse({
        'mensagens': mensagens_data,
        'total': len(mensagens_data)
    })