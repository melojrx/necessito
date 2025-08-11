from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard principal
    path('', views.AdminPanelView.as_view(), name='dashboard'),
    
    # Importação de categorias
    path('import-categories/', views.ImportCategoriesView.as_view(), name='import_categories'),
    
    # Atualização de descrições
    path('update-descriptions/', views.UpdateSubcategoryDescriptionsView.as_view(), name='update_descriptions'),
    
    # População de ícones
    path('populate-icons/', views.PopulateIconsView.as_view(), name='populate_icons'),
    
    # Importação de usuários
    path('import-users/', views.ImportUsersView.as_view(), name='import_users'),
    
    # Geolocalização
    path('geolocalize-users/', views.GeolocalizeUsersView.as_view(), name='geolocalize_users'),
    
    path('update-geolocalization/', views.UpdateGeolocalizationView.as_view(), name='update_geolocalization'),
    
    # API para progresso
    path('api/progress/<str:command_id>/', views.command_progress_api, name='command_progress'),
    path('api/clear-progress/<str:command_id>/', views.clear_command_progress, name='clear_progress'),
]