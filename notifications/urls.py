# notifications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('mark_read/<int:notif_id>/', views.mark_notification_read, name='notification_mark_read'),
    path('mark_all_read/', views.mark_all_read, name='notification_mark_all_read'),
    path('get_notifications/', views.get_notifications, name='get_notifications'),
    path('get_counts/', views.get_notification_counts, name='get_notification_counts'),
]