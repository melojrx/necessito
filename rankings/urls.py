from django.urls import path
from .views import AvaliacaoCreateView

app_name = 'rankings'

urlpatterns = [
    path('avaliar/<int:pk>/', AvaliacaoCreateView.as_view(), name='avaliar_negociacao'),
]
