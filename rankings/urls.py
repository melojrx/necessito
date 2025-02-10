from django.urls import path
from .views import AvaliacaoCreateView

urlpatterns = [
    path('avaliar/<int:pk>/', AvaliacaoCreateView.as_view(), name='avaliar_negociacao'),
]
