from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from core.views import (
    HelpView, 
    HelpStartView, 
    HelpAnnounceView, 
    HelpBudgetView, 
    HelpCommunicationView, 
    HelpRatingsView, 
    HelpSupportView,
    SecurityTipsView,
    TermsOfServiceView,
    PrivacyPolicyView,
    IntellectualPropertyView,
    SitemapView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ads.urls")),
    path("users/", include('users.urls')),
    path('categorias/', include('categories.urls')),
    path('orcamentos/', include('budgets.urls')),
    path('rankings/', include('rankings.urls')),
    path('notifications/', include('notifications.urls')),
    path('buscar/', include('search.urls')),
    path('chat/', include('chat.urls')),
    
    # API com versionamento
    path('api/', include('api.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    
    # Redirecionamento para corrigir logout do DRF
    path('accounts/logout/', RedirectView.as_view(url='/api/logout-redirect/', permanent=False), name='account_logout'),
    
    # Páginas institucionais
    path('dicas-de-seguranca/', SecurityTipsView.as_view(), name='security_tips'),
    path('mapa-do-site/', SitemapView.as_view(), name='sitemap'),
    
    # Páginas legais
    path('termos-de-uso/', TermsOfServiceView.as_view(), name='terms_of_service'),
    path('politica-de-privacidade/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('propriedade-intelectual/', IntellectualPropertyView.as_view(), name='intellectual_property'),
    
    # Central de Ajuda - Página Principal
    path('ajuda/', HelpView.as_view(), name='help'),
    # Alias /help/ -> /ajuda/
    path('help/', RedirectView.as_view(url='/ajuda/', permanent=True), name='help_alias'),
    
    # Central de Ajuda - Seções Específicas
    path('ajuda/comecar/', HelpStartView.as_view(), name='help_start'),
    path('ajuda/anunciar/', HelpAnnounceView.as_view(), name='help_announce'),
    path('ajuda/orcamentos/', HelpBudgetView.as_view(), name='help_budget'),
    path('ajuda/comunicacao/', HelpCommunicationView.as_view(), name='help_communication'),
    path('ajuda/avaliacoes/', HelpRatingsView.as_view(), name='help_ratings'),
    path('ajuda/suporte/', HelpSupportView.as_view(), name='help_support'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)