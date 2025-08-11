from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from users.forms import CustomPasswordResetForm, CustomSetPasswordForm, CustomPasswordChangeForm
from users import views
from users.views import UserUpdateView, UserDetailView, UserProfileDetailView

app_name = 'users'

urlpatterns = [
     path('login/', views.login_view, name='login'), 
     path('register/', views.register_view, name='register'),
     path('logout/', views.logout_view, name='logout'),
    path('complete-profile/', views.complete_profile_view, name='complete_profile'),
     path('minha-conta/<int:pk>/detail/', views.UserDetailView.as_view(), name='minha_conta_detail'),
     path('minha-conta/<int:pk>/update/', views.UserUpdateView.as_view(), name='minha_conta_update'),
     path('perfil/<int:pk>/', views.UserProfileDetailView.as_view(), name='user_profile'),
     path("password_reset/", views.MyPasswordResetView.as_view(template_name="password_reset_form.html", form_class=CustomPasswordResetForm), name="password_reset",),
     path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),  name="password_reset_done",),
     path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html", form_class=CustomSetPasswordForm), name="password_reset_confirm",),
     path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),name="password_reset_complete",), 
     path("password_change/", auth_views.PasswordChangeView.as_view(template_name="password_change_form.html", form_class=CustomPasswordChangeForm, success_url=reverse_lazy("password_change_done")), name="password_change"),
     path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="registration/password_change_done.html"), name="password_change_done"),      
]