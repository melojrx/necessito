from django.urls import path
from .views import NecessidadeSearchAllView

app_name = "search"

urlpatterns = [
    
     path("buscar/", NecessidadeSearchAllView.as_view(),
         name="necessidade_search_all"),]