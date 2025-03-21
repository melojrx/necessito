from django.urls import path
from . import views

urlpatterns = [
    path('mark_read/<int:notif_id>/', views.mark_notification_read, name='notification_mark_read'),
]
