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
from users.forms import BasicUserCreationForm, UserUpdateForm, UserLoginForm, UserCompletionForm
from users.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.db.models import Avg
from django.contrib.auth.decorators import login_required


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
             # A validação do reCAPTCHA falhará aqui também caso o token seja inválido
            messages.error(request, "Verifique seus dados. Email, senha ou reCAPTCHA inválidos.")

    return render(request, 'login.html', {'form': form})

def register_view(request):
    """Cadastro básico (apenas dados essenciais)"""
    if request.method == "POST":
        form = BasicUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            # Não definir is_client/is_supplier ainda
            usuario.save()
            
            # Fazer login automático após cadastro
            login(request, usuario)
            
            messages.success(request, f"Bem-vindo(a), {usuario.first_name}! Complete seu cadastro para ter uma experiência completa.")
            
            # Redirecionar para tela de complemento
            return redirect('complete_profile')
        else:
           # A validação do reCAPTCHA falhará aqui também caso o token seja inválido
            messages.error(request, "Verifique seus dados. Email, senha ou reCAPTCHA inválidos.")
    else:
        form = BasicUserCreationForm()
    
    return render(request, "register.html", {"form": form})

@login_required
def complete_profile_view(request):
    """Tela para completar o perfil após cadastro básico"""
    user = request.user
    
    # Se o usuário já tem is_client ou is_supplier definido, redirecionar para home
    if user.is_client or user.is_supplier:
        messages.info(request, "Seu perfil já está completo!")
        return redirect('home')
    
    if request.method == "POST":
        form = UserCompletionForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "🎉 Cadastro completo! Agora você pode aproveitar todas as funcionalidades da plataforma.")
            return redirect('home')
        else:
            messages.error(request, "Verifique os dados informados.")
    else:
        form = UserCompletionForm(instance=user)
    
    return render(request, "complete_profile.html", {
        "form": form,
        "user": user
    })

def logout_view(request):
    logout(request)
    return redirect('home')

class UserDetailView(DetailView):
    model = User
    template_name = 'minha-conta-detail.html'
    context_object_name = 'user'
    success_url = reverse_lazy('minha_conta_detail')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        avaliacoes = Avaliacao.objects.filter(avaliado=user)
        total_avaliacoes = avaliacoes.count()

        media_estrelas = avaliacoes.aggregate(avg=Avg('media_estrelas'))['avg'] or 0
        media_estrelas = round(media_estrelas, 1)

        context.update({
            'media_estrelas': media_estrelas,
            'total_avaliacoes': total_avaliacoes
        })

        return context

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
        user = self.get_object()

        # ======================
        # BLOCO DE AVALIAÇÕES
        # ======================
        avaliacoes = Avaliacao.objects.filter(avaliado=user)
        total_avaliacoes = avaliacoes.count()
        media_estrelas = avaliacoes.aggregate(avg=Avg('media_estrelas'))['avg'] or 0
        media_estrelas = round(media_estrelas, 1)

        # Cálculo de estrelas cheias, meia estrela, vazias
        estrelas_cheias = int(media_estrelas)
        estrelas_meia = 1 if (media_estrelas - estrelas_cheias) >= 0.5 else 0
        estrelas_vazias = 5 - estrelas_cheias - estrelas_meia

        # ======================
        # BLOCO DE ANÚNCIOS
        # ======================
        query_params = self.request.GET

        anuncios = Necessidade.objects.filter(cliente=user)

        search_query = query_params.get('search', '')
        if search_query:
            anuncios = anuncios.filter(descricao__icontains=search_query)

        categoria_id = query_params.get('categoria')
        if categoria_id:
            anuncios = anuncios.filter(categoria_id=categoria_id)

        cidade = query_params.get('cidade', '')
        if cidade:
            anuncios = anuncios.filter(cliente__cidade__icontains=cidade)

        order_by = query_params.get('order_by', '-data_criacao')
        anuncios = anuncios.order_by(order_by)

        # Total de anúncios nos últimos 180 dias
        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        total_anuncios_6meses = Necessidade.objects.filter(
            cliente=user,
            data_criacao__gte=six_months_ago
        ).count()

        categorias_disponiveis = anuncios.values('categoria__id', 'categoria__nome').distinct()
        cidades_disponiveis = anuncios.values('cliente__cidade').distinct()

        # ======================
        # ATUALIZA O CONTEXTO
        # ======================
        context.update({
            # Avaliações
            'avaliacoes': avaliacoes,
            'total_avaliacoes': total_avaliacoes,
            'media_estrelas': media_estrelas,
            'estrelas_cheias': estrelas_cheias,
            'estrelas_meia': estrelas_meia,
            'estrelas_vazias': estrelas_vazias,

            # Anúncios
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

from django.contrib.auth import views as auth_views

class MyPasswordResetView(auth_views.PasswordResetView):
    # Força o domínio a ser "necessito.br" no link enviado
    domain_override = "necessito.br"

    # Altera o remetente
    from_email = "Necessito <no-reply@necessito.br>"

    # Personaliza o assunto
    subject_template_name = "password_reset_subject.txt"

    # Personaliza o corpo do e-mail (formato texto)
    email_template_name = "password_reset_email.html"

    # Caso queira adicionar um template HTML:
    # html_email_template_name = "password_reset_email_html.html"
    
    # É possível também definir success_url, etc. se quiser
