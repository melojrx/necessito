# notifications/views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from .models import Notification

@login_required
def mark_notification_read(request, notif_id):
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.is_read = True
    notification.save()

    # Se for uma requisição AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # Redirecionar para a página anterior ou para a página do anúncio
    if notification.necessidade:
        return redirect('necessidade_detail', pk=notification.necessidade.id)

    # Se não houver referrer, redireciona para a home
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('home')

@login_required
def mark_all_read(request):
    """Marca todas as notificações do usuário como lidas"""
    request.user.notifications.filter(is_read=False).update(is_read=True)

    # Redirecionar para a página anterior
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('home')

@login_required
def get_notifications(request):
    """Retorna as notificações paginadas do usuário"""
    # Se apenas a contagem for solicitada
    if request.GET.get('count_only') == 'true':
        unread_count = request.user.notifications.filter(is_read=False).count()
        return JsonResponse({'unread_count': unread_count})

    page = request.GET.get('page', 1)
    notifications = request.user.notifications.all().order_by('-created_at')  # Ordenar por data de criação (mais recentes primeiro)

    # Configurar paginação - 5 notificações por página (alterado de 10 para 5)
    paginator = Paginator(notifications, 5)  # Alterado para 5
    page_obj = paginator.get_page(page)

    # Renderizar apenas o HTML das notificações
    notifications_html = render_to_string(
        'notifications/notifications_list.html',
        {'page_obj': page_obj, 'request': request}
    )

    return JsonResponse({
        'html': notifications_html,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })

@login_required
def get_notification_counts(request):
    """Retorna contadores de notificações e mensagens em tempo real"""
    from chat.models import ChatRoom, ChatMessage
    from django.db.models import Q
    
    # Contar notificações não lidas
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    
    # Contar mensagens não lidas
    unread_messages = ChatMessage.objects.filter(
        chat_room__in=ChatRoom.objects.filter(
            Q(cliente=request.user) | Q(fornecedor=request.user),
            ativo=True
        ),
        lida=False
    ).exclude(remetente=request.user).count()
    
    return JsonResponse({
        'unread_notifications': unread_notifications,
        'unread_messages': unread_messages,
        'total_unread': unread_notifications + unread_messages
    })