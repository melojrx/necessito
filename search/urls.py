from django.urls import path
from .views import NecessidadeSearchAllView, autocomplete_search

app_name = "search"

urlpatterns = [
    path("buscar/", NecessidadeSearchAllView.as_view(),
         name="necessidade_search_all"),
    path("autocomplete/", autocomplete_search, 
         name="autocomplete_search"),
]