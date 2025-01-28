from django.urls import path
from .views import SubmeterOrcamentoView, budgetListView, budgetDetailView, BudgetUpdateView, budgetDeleteView

urlpatterns = [
    path('submeter/<int:pk>/', SubmeterOrcamentoView.as_view(), name='submeter_orcamento'),
    path('budgets/', budgetListView.as_view(), name='budget_list'),
    path('budgets/<int:pk>/', budgetDetailView.as_view(), name='budget_detail'),
    path('budgets/<int:pk>/editar/', BudgetUpdateView.as_view(), name='budget_update'),
    path('budgets/<int:pk>/excluir/', budgetDeleteView.as_view(), name='budget_delete'),
]
