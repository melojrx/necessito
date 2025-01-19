from django.urls import path
from .views import SubmeterOrcamentoView

urlpatterns = [
    path('submeter/<int:pk>/', SubmeterOrcamentoView.as_view(), name='submeter_orcamento'),
]
