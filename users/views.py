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
from users.forms import CustomUserCreationForm, UserUpdateForm, UserLoginForm, UserCompletionForm
from users.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.db.models import Avg


@csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect('ads:home')

    form = UserLoginForm()  # Form vazio para GET

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, "Login realizado com sucesso!")
            return redirect('ads:home')  
        else:
             # A validação do reCAPTCHA falhará aqui também caso o token seja inválido
            messages.error(request, "Verifique seus dados. Email, senha ou reCAPTCHA inválidos.")

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
            return redirect('users:login')
        else:
           # A validação do reCAPTCHA falhará aqui também caso o token seja inválido
            messages.error(request, "Verifique seus dados. Email, senha ou reCAPTCHA inválidos.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, "register.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('ads:home')

class UserDetailView(DetailView):
    model = User
    template_name = 'minha-conta-detail.html'
    context_object_name = 'user'
    success_url = reverse_lazy('users:minha_conta_detail')

    def dispatch(self, request, *args, **kwargs):
        # Verificar autenticação no dispatch (antes de qualquer processamento)
        if not request.user.is_authenticated:
            return redirect('users:login')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Pegar o ID da URL
        pk = self.kwargs.get('pk')
        
        # Verificar se o usuário está autenticado
        if not self.request.user.is_authenticated:
            from django.http import Http404
            raise Http404("Usuário não autenticado")
        
        # Buscar o usuário pelo ID
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            from django.http import Http404
            raise Http404("Usuário não encontrado")
        
        # Verificar se o usuário pode ver este perfil
        # Por enquanto, permitir que qualquer usuário autenticado veja qualquer perfil
        # Você pode adicionar lógica de permissão aqui se necessário
        
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Usar self.object que já foi definido pelo Django DetailView
        user = self.object
        
        # Não precisa verificar is_authenticated pois User objects sempre são authenticated
        # apenas AnonymousUser não é authenticated

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
        return reverse('users:minha_conta_detail', kwargs={'pk': self.object.pk})
    
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
from django.conf import settings

class MyPasswordResetView(auth_views.PasswordResetView):
    # Usar domínio dinâmico obtido do request
    domain_override = None

    # Altera o remetente para usar a configuração padrão
    from_email = settings.DEFAULT_FROM_EMAIL

    # Personaliza o assunto
    subject_template_name = "password_reset_subject.txt"

    # Personaliza o corpo do e-mail (formato texto)
    email_template_name = "password_reset_email.html"
    
    # Template HTML para e-mail mais bonito (opcional - fallback para texto se não suportado)
    html_email_template_name = "password_reset_email_html.html"
    
    # URL de sucesso com namespace correto
    success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        # Garante domínio dinâmico com base no host atual
        form.save(
            domain_override=self.request.get_host(),
            use_https=self.request.is_secure(),
            from_email=self.from_email,
            email_template_name=self.email_template_name,
            subject_template_name=self.subject_template_name,
            html_email_template_name=self.html_email_template_name,
            request=self.request,
        )
        return redirect(self.get_success_url())

@csrf_exempt
def complete_profile_view(request):
    """
    View para completar o perfil do usuário.
    Permite escolher se é cliente, fornecedor ou ambos.
    """
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    # Se o perfil já está completo, redireciona para home
    if request.user.is_client or request.user.is_supplier:
        messages.info(request, "Seu perfil já está completo!")
        return redirect('ads:home')
    
    if request.method == 'POST':
        form = UserCompletionForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                "Perfil completado com sucesso! Agora você tem acesso completo à plataforma."
            )
            return redirect('ads:home')
        else:
            messages.error(request, "Verifique os dados informados.")
    else:
        form = UserCompletionForm(instance=request.user)
    
    return render(request, "complete_profile.html", {"form": form})

    # Caso queira adicionar um template HTML:
    # html_email_template_name = "password_reset_email_html.html"
    
    # É possível também definir success_url, etc. se quiser
