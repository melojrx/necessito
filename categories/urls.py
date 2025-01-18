from django.urls import path
from .views import (
    CategoryListView,
    CategoryDetailView,
    SubCategoryListView,
    SubCategoryDetailView,
    subcategorias_json
)

urlpatterns = [
    path('<int:category_id>/subcats-json/', subcategorias_json, name='subcats_json'),
    # Listagem de todas as categorias
    path('categorias/', CategoryListView.as_view(), name='category_list'),

    # Detalhe de uma categoria específica (opcional)
    path('categorias/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),

    # Listagem de subcategorias (opcionalmente filtrada por categoria)
    path('subcategorias/', SubCategoryListView.as_view(), name='subcategory_list'),

    # Opcionalmente, se quiser passar o category_id
    path('categorias/<int:category_id>/subcategorias/', SubCategoryListView.as_view(), name='subcategories_by_category'),

    # Detalhe de uma subcategoria específica (opcional)
    path('subcategorias/<int:pk>/', SubCategoryDetailView.as_view(), name='subcategory_detail'),
]
