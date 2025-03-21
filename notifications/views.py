# notifications/views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from notifications.models import Notification

@login_required
def mark_notification_read(request, notif_id):
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('home')  # ou redirecionar para onde você quiser
