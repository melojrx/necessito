from django.urls import path
from .views import (
    FinalizarAnuncioView, HomeView, NecessidadeListView, NecessidadeCreateView,
    NecessidadeDetailView, NecessidadeUpdateView, NecessidadeDeleteView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('necessidades/', NecessidadeListView.as_view(), name='necessidade_list'),
    path('necessidades/nova/', NecessidadeCreateView.as_view(), name='necessidade_create'),
    path('necessidades/<int:pk>/', NecessidadeDetailView.as_view(), name='necessidade_detail'),
    path('necessidades/<int:pk>/editar/', NecessidadeUpdateView.as_view(), name='necessidade_update'),
    path('necessidades/<int:pk>/excluir/', NecessidadeDeleteView.as_view(), name='necessidade_delete'),
    path('necessidades/<int:pk>/finalizar/', FinalizarAnuncioView.as_view(), name='finalizar_anuncio'),
]

