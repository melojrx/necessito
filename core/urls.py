from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core import settings
from core.views import HelpView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ads.urls")),
    path("users/", include('users.urls')),
    path('categorias/', include('categories.urls')),
    path('orcamentos/', include('budgets.urls')),
    path('rankings/', include('rankings.urls')),
    path('notifications/', include('notifications.urls')),
    path('buscar/', include('search.urls')),
    path('api/', include('api.urls')),
    
    # Páginas institucionais
    path('ajuda/', HelpView.as_view(), name='help'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)