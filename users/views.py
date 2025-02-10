import datetime
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from ads.models import Necessidade
from rankings.models import Avaliacao
from users.forms import CustomUserCreationForm, UserUpdateForm, UserLoginForm
from users.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.db.models import Avg

def minha_conta(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    # Calcular média e total de avaliações
    avaliacoes = Avaliacao.objects.filter(avaliado=user)
    total_avaliacoes = avaliacoes.count()
    media_estrelas = avaliacoes.aggregate(avg=Avg('estrelas'))['avg'] or 0
    media_estrelas = round(media_estrelas, 1)  # Arredonda para 1 casa decimal
    
    context = {
        'user': user,
        'media_estrelas': media_estrelas,
        'total_avaliacoes': total_avaliacoes,
    }
    
    return render(request, 'minha-conta-detail.html', context)


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
    
import datetime
from django.utils import timezone

class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user_profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()  # Usuário do perfil
        query_params = self.request.GET

        # Filtro inicial de anúncios
        anuncios = Necessidade.objects.filter(cliente=user)

        # Filtros
        search_query = query_params.get('search', '')
        if search_query:
            anuncios = anuncios.filter(descricao__icontains=search_query)

        categoria_id = query_params.get('categoria')
        if categoria_id:
            anuncios = anuncios.filter(categoria_id=categoria_id)

        cidade = query_params.get('cidade', '')
        if cidade:
            anuncios = anuncios.filter(cliente__cidade__icontains=cidade)

        # Ordenação
        order_by = query_params.get('order_by', '-data_criacao')  # Default: mais recentes
        anuncios = anuncios.order_by(order_by)

        # Total de anúncios nos últimos 180 dias
        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        total_anuncios_6meses = Necessidade.objects.filter(
            cliente=user,
            data_criacao__gte=six_months_ago
        ).count()

        # Categorias e cidades disponíveis para os filtros
        categorias_disponiveis = anuncios.values('categoria__id', 'categoria__nome').distinct()
        cidades_disponiveis = anuncios.values('cliente__cidade').distinct()

        context.update({
            'anuncios': anuncios,
            'categorias': categorias_disponiveis,
            'cidades': cidades_disponiveis,
            'total_anuncios_6meses': total_anuncios_6meses,
            'search_query': search_query,
            'categoria_id': categoria_id,
            'cidade': cidade,
            'order_by': order_by,
        })
        return context

