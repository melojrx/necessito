from django.urls import path
from .views import (CategoryListView, CategoryDetailView, SubCategoryListView, SubCategoryDetailView, subcategorias_json)

urlpatterns = [
    path('<int:category_id>/subcats-json/', subcategorias_json, name='subcats_json'),
    path('categorias/', CategoryListView.as_view(), name='category_list'),
    path('categorias/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('subcategorias/', SubCategoryListView.as_view(), name='subcategory_list'),
    path('categorias/<int:category_id>/subcategorias/', SubCategoryListView.as_view(), name='subcategories_by_category'),
    path('subcategorias/<int:pk>/', SubCategoryDetailView.as_view(), name='subcategory_detail'),
]
