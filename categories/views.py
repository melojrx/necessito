from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Categoria, SubCategoria
from django.http import JsonResponse


def subcategorias_json(request, category_id):
    """
    Retorna as subcategorias de uma dada categoria em formato JSON.
    Ex: /categorias/1/subcats-json/
    """
    subcats = SubCategoria.objects.filter(categoria_id=category_id)
    data = []
    for sc in subcats:
        data.append({
            'id': sc.id,
            'nome': sc.nome,
        })
    return JsonResponse({'subcategorias': data})

# ========== CATEGORIAS ==========

class CategoryListView(ListView):
    """Lista todas as categorias."""
    model = Categoria
    template_name = 'categories/category_list.html'  # ou 'category_list.html'
    context_object_name = 'categorias'
    # Por padrão, o ListView retorna `object_list` no template;
    # definimos context_object_name para algo mais amigável (categorias).

    # Se quiser, pode customizar a ordem:
    # ordering = ['-id']


class CategoryDetailView(DetailView):
    """Exibe detalhes de uma categoria específica."""
    model = Categoria
    template_name = 'categories/category_detail.html'
    context_object_name = 'categoria'
    # Aqui, a view pega a PK da URL (pk=<int:pk>)


# ========== SUBCATEGORIAS ==========

class SubCategoryListView(ListView):
    """Lista subcategorias, podendo filtrar por categoria."""
    model = SubCategoria
    template_name = 'categories/subcategory_list.html'
    context_object_name = 'subcategorias'

    def get_queryset(self):
        # Se vier 'category_id' na URL, filtra;
        # caso contrário, retorna todas as subcategorias
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        if category_id:
            queryset = queryset.filter(categoria__id=category_id)
        return queryset


class SubCategoryDetailView(DetailView):
    """Exibe detalhes de uma subcategoria específica."""
    model = SubCategoria
    template_name = 'categories/subcategory_detail.html'
    context_object_name = 'subcategoria'
