import datetime
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from ads.models import Necessidade
from users.forms import CustomUserCreationForm, UserUpdateForm, UserLoginForm
from users.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView


@csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = UserLoginForm()  # Form vazio para GET

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, "Login realizado com sucesso!")
            return redirect('home')  
        else:
            messages.error(request, "Email ou senha inválidos.")  # Ou você pode confiar no form para exibir o erro

    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_client = form.cleaned_data.get('is_client', False)
            usuario.is_supplier = form.cleaned_data.get('is_supplier', False)
            usuario.save()
            messages.success(request, "Registrado com sucesso! Faça login para começar.")
            return redirect('login')
        else:
            messages.error(request, "Erro ao registrar. Verifique os dados informados.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, "register.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('home')

class UserDetailView(DetailView):
    model = User
    form_class = UserUpdateForm
    template_name = 'minha-conta-detail.html'
    success_url = reverse_lazy('minha_conta_detail')
    
    def get_object(self, queryset=None):
        # Retorna o user que está logado
        return self.request.user

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'minha-conta-update.html'
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        # Aqui, 'self.object' é o usuário atualizado
        return reverse('minha_conta_detail', kwargs={'pk': self.object.pk})
    
class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user_profile.html'
    context_object_name = 'user'
    
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            user = context['user']
            
            six_months_ago = timezone.now() - datetime.timedelta(days=180)
            
            # Filtra os anúncios criados depois de 'six_months_ago'
            total_anuncios_6meses = Necessidade.objects.filter(
                cliente=user,
                data_criacao__gte=six_months_ago
            ).count()

            context['total_anuncios_6meses'] = total_anuncios_6meses
            return context