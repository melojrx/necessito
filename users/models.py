"""
models.py  –  App users
Definição do modelo de usuário customizado (e gerenciador) utilizado no sistema.
- Autenticação por e-mail
- Campos de endereço e geolocalização (lat/lon) via CEP
- Validação de CPF usando utilitário próprio
"""

import requests
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.forms import ValidationError
from django.db.models import Avg 
from categories.models import Categoria
from django.conf import settings
from users.utils import validate_cpf


# -----------------------------------------------------------------------------#
#  GERENCIADOR DE USUÁRIO CUSTOMIZADO
# -----------------------------------------------------------------------------#
class UserManager(BaseUserManager):
    """
    Substitui o gerenciador padrão para permitir criação por e-mail
    e busca automática de coordenadas (lat/lon) a partir do CEP.
    """

    def _set_lat_lon_from_cep(self, user, cep: str) -> None:
        """
        Consulta o serviço Nominatim (OpenStreetMap) para obter
        latitude e longitude aproximadas do CEP informado.
        - Salva valores diretamente nos campos user.lat / user.lon
        - Em produção, idealmente tratar logs de exceção.
        """
        cep = cep.replace("-", "").strip()
        if not cep:
            return

        try:
            resp = requests.get(
                f"https://nominatim.openstreetmap.org/search?format=json&q={cep}",
                headers={"User-Agent": "DjangoApp"},
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    user.lat = float(data[0]["lat"])
                    user.lon = float(data[0]["lon"])
        except Exception:
            # TODO: registrar erro em log
            pass

    def create_user(self, email, password=None, **extra_fields):
        """Cria e retorna um usuário comum."""
        if not email:
            raise ValueError("O campo e-mail é obrigatório")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        # Preenche lat/lon se CEP fornecido
        self._set_lat_lon_from_cep(user, extra_fields.get("cep", ""))

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e retorna um superusuário (admin)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário precisa ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# -----------------------------------------------------------------------------#
#  MODELO DE USUÁRIO
# -----------------------------------------------------------------------------#
class User(AbstractUser):
    """
    Usuário customizado
    - Autenticação por e-mail (USERNAME_FIELD = email)
    - Campos extras: telefone, endereço, geolocalização, foto, etc.
    - Flags de perfil (cliente / fornecedor)
    """

    # Remover campo username padrão
    username = None

    # Flags de papéis
    is_client = models.BooleanField("É cliente?", default=False)
    is_supplier = models.BooleanField("É fornecedor?", default=False)

    # Identificação
    first_name = models.CharField("Nome", max_length=100)
    last_name = models.CharField("Sobrenome", max_length=100)
    email = models.EmailField("E-mail", unique=True, max_length=255)

    # Contato
    telefone = models.CharField("Telefone", max_length=15, blank=True)

    # Informações pessoais / endereço
    data_nascimento = models.DateField("Data de nascimento", null=True, blank=True)
    endereco = models.TextField("Endereço", blank=True)
    bairro = models.CharField("Bairro", max_length=100, blank=True)
    cep = models.CharField("CEP", max_length=15, blank=True)
    cidade = models.CharField("Cidade", max_length=100, blank=True)
    estado = models.CharField(
        "Estado (UF)",
        max_length=2,
        blank=True,
        validators=[RegexValidator(r"^[A-Z]{2}$", "Use siglas como CE, SP, RJ …")],
    )

    # Documentos
    cpf = models.CharField("CPF", max_length=14, unique=True, null=True, blank=True)
    cnpj = models.CharField("CNPJ", max_length=18, unique=True, null=True, blank=True)

    # Geolocalização
    lat = models.FloatField("Latitude", null=True, blank=True)
    lon = models.FloatField("Longitude", null=True, blank=True)

    # Preferências
    preferred_categories = models.ManyToManyField(
        Categoria,
        blank=True,
        related_name="users_preferred",
        verbose_name="Categorias preferidas",
    )

    # Arquivos & mídias
    comprovante_endereco = models.FileField(
        "Comprovante de endereço", upload_to="comprovantes/", null=True, blank=True
    )
    foto = models.ImageField(
        "Foto de perfil",
        upload_to="fotos_usuarios/",
        null=True,
        blank=True,
        help_text="Envie uma imagem quadrada (recomendado 400×400 px)",
    )

    # Verificação de e-mail
    email_verified = models.BooleanField("E-mail verificado", default=True)
    email_verification_token = models.CharField("Token de verificação", max_length=100, blank=True, null=True)

    # Metadados
    date_joined = models.DateTimeField("Data de cadastro", auto_now_add=True)

    # Configurações de autenticação
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    # -------------------- Métodos utilitários -------------------- #
    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    # Validações personalizadas
    def clean(self):
        """
        Chamado por ModelForm.save() ou manualmente via full_clean().
        Utiliza utilitário validate_cpf para garantir formato correto.
        """
        super().clean()
        if self.cpf:
            try:
                self.cpf = validate_cpf(self.cpf)  # armazena apenas dígitos
            except ValidationError as e:
                raise ValidationError({"cpf": e.message})

    # -------------------- Propriedades auxiliares -------------------- #
    @property
    def foto_url(self) -> str:
        """
        Retorna URL da foto de perfil ou um avatar padrão.
        """
        from django.conf import settings as django_settings
        return self.foto.url if self.foto else f"{django_settings.MEDIA_URL}fotos_usuarios/avatar.png"

    @property
    def result_type(self) -> str:
        """
        Tipo de resultado usado em buscas / APIs.
        """
        return "user"

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["-date_joined"]
        
# ---------------------------------------------------------------------
    #  MÉTRICAS DE AVALIAÇÃO
    # ---------------------------------------------------------------------
    def get_media_avaliacoes(self, tipo=None):
        """
        Retorna a média geral (estrelas) das avaliações recebidas.
        Se `tipo` for informado ('cliente' ou 'fornecedor'),
        filtra apenas essas avaliações.
        """
        avaliacoes = self.avaliacoes_recebidas.all()
        if tipo:
            avaliacoes = avaliacoes.filter(tipo_avaliacao=tipo)

        if not avaliacoes.exists():
            return None

        return avaliacoes.aggregate(Avg("media_estrelas"))["media_estrelas__avg"]

    def get_criterios_media(self, tipo=None):
        """
        Retorna um dicionário com a média de estrelas por critério
        para todas as avaliações recebidas.
        Exemplo de retorno:
        {
            'rapidez_respostas': { 'label': 'Rapidez nas respostas', 'media': 4.2 },
            'qualidade_produto': { 'label': 'Qualidade do Produto',  'media': 4.8 },
            …
        }
        """
        avaliacoes = self.avaliacoes_recebidas.all()
        if tipo:
            avaliacoes = avaliacoes.filter(tipo_avaliacao=tipo)

        if not avaliacoes.exists():
            return {}

        from rankings.models import AvaliacaoCriterio  # import local evita ciclos

        criterios = AvaliacaoCriterio.objects.filter(avaliacao__in=avaliacoes)

        resultado = {}
        for criterio_value, criterio_label in AvaliacaoCriterio.CRITERIO_CHOICES:
            criterios_filtrados = criterios.filter(criterio=criterio_value)
            if criterios_filtrados.exists():
                media = criterios_filtrados.aggregate(Avg("estrelas"))["estrelas__avg"]
                resultado[criterio_value] = {
                    "label": criterio_label,
                    "media": media,
                }
        return resultado
    
    # ---------------------------------------------------------------------
    #  SISTEMA DE BADGES DE CONFIANÇA
    # ---------------------------------------------------------------------
    def get_badges(self):
        """
        Retorna lista de badges de confiança baseado no perfil e atividade do usuário.
        """
        from datetime import timedelta
        from django.utils import timezone
        
        badges = []
        
        # Badge: Identidade Verificada
        if self.email_verified and self.cpf:
            badges.append({
                'icon': 'fas fa-check-circle',
                'label': 'Identidade Verificada',
                'class': 'badge-verified',
                'color': 'success'
            })
        
        # Badge: Usuário Ativo (cadastrado há mais de 30 dias)
        if self.date_joined < timezone.now() - timedelta(days=30):
            badges.append({
                'icon': 'fas fa-star',
                'label': 'Usuário Experiente',
                'class': 'badge-experienced',
                'color': 'primary'
            })
        
        # Badge: Fornecedor Verificado
        if self.is_supplier and self.cnpj:
            badges.append({
                'icon': 'fas fa-briefcase',
                'label': 'Fornecedor Profissional',
                'class': 'badge-professional',
                'color': 'info'
            })
        
        # Badge: Avaliação Alta (média >= 4.5)
        media_avaliacoes = self.get_media_avaliacoes()
        if media_avaliacoes and media_avaliacoes >= 4.5:
            badges.append({
                'icon': 'fas fa-trophy',
                'label': f'Excelente ({media_avaliacoes:.1f}★)',
                'class': 'badge-excellent',
                'color': 'warning'
            })
        
        # Badge: Muitas avaliações (mais de 10)
        num_avaliacoes = self.avaliacoes_recebidas.count()
        if num_avaliacoes >= 10:
            badges.append({
                'icon': 'fas fa-users',
                'label': f'{num_avaliacoes}+ Avaliações',
                'class': 'badge-popular',
                'color': 'secondary'
            })
        
        # Badge: Cliente Frequente (mais de 5 necessidades)
        if self.is_client:
            num_necessidades = self.necessidades.count()
            if num_necessidades >= 5:
                badges.append({
                    'icon': 'fas fa-medal',
                    'label': 'Cliente Frequente',
                    'class': 'badge-frequent',
                    'color': 'purple'
                })
        
        # Badge: Fornecedor Ativo (mais de 10 orçamentos)
        if self.is_supplier:
            num_orcamentos = self.orcamentos.count()
            if num_orcamentos >= 10:
                badges.append({
                    'icon': 'fas fa-hammer',
                    'label': 'Fornecedor Ativo',
                    'class': 'badge-active-supplier',
                    'color': 'dark'
                })
        
        return badges
    
    @property
    def trust_score(self):
        """
        Calcula um score de confiança baseado nos badges e atividade.
        Retorna um valor entre 0 e 100.
        """
        score = 0
        
        # Base score por estar verificado
        if self.email_verified:
            score += 20
        
        # Score por documentos
        if self.cpf:
            score += 15
        if self.cnpj:
            score += 10
            
        # Score por avaliações
        media_avaliacoes = self.get_media_avaliacoes()
        if media_avaliacoes:
            score += min(media_avaliacoes * 10, 30)  # máximo 30 pontos
        
        # Score por atividade
        num_avaliacoes = self.avaliacoes_recebidas.count()
        score += min(num_avaliacoes * 2, 20)  # máximo 20 pontos
        
        # Score por tempo de cadastro
        from datetime import timedelta
        from django.utils import timezone
        days_since_joined = (timezone.now() - self.date_joined).days
        score += min(days_since_joined / 10, 15)  # máximo 15 pontos
        
        return min(score, 100)  # máximo 100 pontos
