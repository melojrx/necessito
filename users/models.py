from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.forms import ValidationError
from django.core.validators import RegexValidator
from categories.models import Categoria
from core import settings
from users.utils import validate_cpf

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O campo email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário precisa ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  # Remove o campo username
    is_client = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=255)
    telefone = models.CharField(max_length=15, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    endereco = models.TextField(blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cep = models.CharField(max_length=15, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True, validators=[RegexValidator(r'^[A-Z]{2}$', 'Use siglas como CE, SP, RJ …')])
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True)
    preferred_categories = models.ManyToManyField(
        Categoria,
        blank=True,
        related_name='users_preferred'
    )
    comprovante_endereco = models.FileField(upload_to='comprovantes/', blank=True, null=True)
    foto = models.ImageField(
        upload_to='fotos_usuarios/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil',
        help_text='Envie uma imagem quadrada para melhor visualização (recomendado 400x400px)'
    )
    date_joined = models.DateTimeField('date joined', auto_now_add=True)

    USERNAME_FIELD = 'email'  # Define email como identificador principal
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name
    
    def clean(self):
        """
        Validações do Model (chamadas quando form.is_valid() -> form.save()
        ou se chamarmos user.full_clean() manualmente).
        """
        super().clean()
        if self.cpf:  # Se o campo estiver preenchido
            # Use nossa função validate_cpf
            try:
                # Se for válido, armazenar apenas dígitos
                self.cpf = validate_cpf(self.cpf)
            except ValidationError as e:
                # Repassa erro para o Model
                raise ValidationError({'cpf': e.message})
    @property
    def foto_url(self):
        if self.foto:
            return self.foto.url
        return f'{settings.MEDIA_URL}fotos_usuarios/avatar.png'
    
    @property
    def result_type(self):
        return 'user'
