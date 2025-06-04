from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Lista de chats
    path('', views.lista_chats, name='lista_chats'),
    
    # Chat específico
    path('<int:chat_id>/', views.chat_detail, name='chat_detail'),
    
    # APIs
    path('<int:chat_id>/enviar/', views.enviar_mensagem, name='enviar_mensagem'),
    path('<int:chat_id>/buscar-novas/', views.buscar_mensagens_novas, name='buscar_mensagens_novas'),
    
    # Iniciar chat
    path('iniciar/<int:necessidade_id>/', views.iniciar_chat, name='iniciar_chat'),
]