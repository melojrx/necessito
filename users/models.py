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
from core import settings
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
        return self.foto.url if self.foto else f"{settings.MEDIA_URL}fotos_usuarios/avatar.png"

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
