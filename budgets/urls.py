from django.urls import path
from .views import OrcamentoAceitarView, OrcamentoFornecedorAceitarView, OrcamentoRejeitarView, SubmeterOrcamentoView, budgetListView, budgetDetailView, BudgetUpdateView, budgetDeleteView, export_orcamento_pdf

urlpatterns = [
    path('submeter/<int:pk>/', SubmeterOrcamentoView.as_view(), name='submeter_orcamento'),
    path('budgets/<int:pk>/aceitar/', OrcamentoAceitarView.as_view(), name='aceitar_orcamento'),
    path('budgets/<int:pk>/aceitar_fornecedor/', OrcamentoFornecedorAceitarView.as_view(), name='aceitar_orcamento_fornecedor'),
    path('budgets/<int:pk>/rejeitar/', OrcamentoRejeitarView.as_view(), name='rejeitar_orcamento'),
    path('budgets/', budgetListView.as_view(), name='budget_list'),
    path('budgets/<int:pk>/', budgetDetailView.as_view(), name='budget_detail'),
    path('budgets/<int:pk>/editar/', BudgetUpdateView.as_view(), name='budget_update'),
    path('budgets/<int:pk>/excluir/', budgetDeleteView.as_view(), name='budget_delete'),
    path('orcamento/<int:pk>/export-pdf/', export_orcamento_pdf, name='export_orcamento_pdf'),
]
