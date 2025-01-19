from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ads.urls")),
    path("users/", include('users.urls')),
    path('categorias/', include('categories.urls')),
    path('orcamentos/', include('budgets.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)