from django.urls import path
from users import views
from users.views import UserUpdateView, UserDetailView, UserProfileDetailView

urlpatterns = [
     path('login/', views.login_view, name='login'), 
     path('register/', views.register_view, name='register'),
     path('logout/', views.logout_view, name='logout'),
     path('minha-conta/<int:pk>/detail/', views.UserDetailView.as_view(), name='minha_conta_detail'),
     path('minha-conta/<int:pk>/update/', views.UserUpdateView.as_view(), name='minha_conta_update'),
     path('perfil/<int:pk>/', views.UserProfileDetailView.as_view(), name='user_profile'),
            
]