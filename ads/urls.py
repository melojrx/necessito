from django.urls import path
from .views import (
    FinalizarAnuncioView, HomeView, NecessidadeListView, NecessidadeCreateView,
    NecessidadeDetailView, NecessidadeUpdateView, NecessidadeDeleteView, AnunciosPorCategoriaListView, DashboardView, anuncios_geolocalizados, enviar_mensagem, geolocalizar_usuario, dados_compartilhamento
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('necessidades/', NecessidadeListView.as_view(), name='necessidade_list'),
    path('necessidades/nova/', NecessidadeCreateView.as_view(), name='necessidade_create'),
    path('necessidades/<int:pk>/', NecessidadeDetailView.as_view(), name='necessidade_detail'),
    path('necessidades/<int:pk>/editar/', NecessidadeUpdateView.as_view(), name='necessidade_update'),
    path('necessidades/<int:pk>/excluir/', NecessidadeDeleteView.as_view(), name='necessidade_delete'),
    path('necessidades/<int:pk>/finalizar/', FinalizarAnuncioView.as_view(), name='finalizar_anuncio'),
    path('necessidades/categoria/<int:category_id>/', AnunciosPorCategoriaListView.as_view(), name='anuncios_por_categoria'),
    path('necessidades/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('necessidade/<int:pk>/enviar-mensagem/', enviar_mensagem, name='enviar_mensagem'),
    path('necessidade/<int:pk>/compartilhar/', dados_compartilhamento, name='dados_compartilhamento'),
    path('api/anuncios-geolocalizados/', anuncios_geolocalizados, name='anuncios_geolocalizados'),
    path('api/geolocalizar-usuario/', geolocalizar_usuario, name='geolocalizar_usuario'),

]

