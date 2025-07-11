from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from users.models import User
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from categories.models import Categoria
from users.utils import validate_cpf, validate_password_strength

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemplo@indicaai.com'
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '********'
        })
    )
    
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            attrs={
                'data-theme': 'light',  # ou 'dark'
                'data-size': 'normal'   # ou 'compact'
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Email ou senha inválidos.")
            cleaned_data["user"] = user  # Guardar o user para uso na view
        return cleaned_data

class BasicUserCreationForm(UserCreationForm):
    """Formulário simplificado para cadastro inicial (apenas dados básicos)"""
    password1 = forms.CharField(
        label="Senha", 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )
    password2 = forms.CharField(
        label="Confirmação de Senha", 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme sua senha'
        })
    )

    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            attrs={
                'data-theme': 'light',
                'data-size': 'normal'
            }
        )
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'email': 'E-mail',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemplo@indicaai.com'
            }),
        }

    def clean_email(self):
        """
        Valida que o e-mail não está sendo usado por outro usuário.
        """
        email = self.cleaned_data.get('email')
        if email:
            # Verificar se já existe um usuário com este e-mail
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "Este e-mail já está sendo usado por outro usuário. "
                    "Tente fazer login ou use outro e-mail."
                )
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem!")
        return password2

    def clean_password1(self):
        """
        Valida a força da senha usando critérios de segurança.
        """
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                validate_password_strength(password1)
            except forms.ValidationError as e:
                # Re-lançar com as mensagens de validação
                raise forms.ValidationError(e.messages)
        return password1

class UserCompletionForm(forms.ModelForm):
    """Formulário para completar o perfil após cadastro básico"""
    
    # Campo para escolha do tipo de usuário com design atrativo
    USER_TYPE_CHOICES = [
        ('client', 'Anunciante - Publico necessidades'),
        ('supplier', 'Fornecedor - Ofereço produtos/serviços'),
        ('both', 'Ambos - Anuncio e forneço')
    ]
    
    user_type = forms.ChoiceField(
        label="Como você quer usar a plataforma?",
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        required=True
    )
    
    # Campo ManyToMany manual, para permitir escolha de múltiplas categorias
    preferred_categories = forms.ModelMultipleChoiceField(
        label="Categorias de Interesse (Opcional)",
        queryset=Categoria.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-select',  
                'size': 5,
                'placeholder': 'Escolha até 2 categorias'              
            }
        ),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'user_type',  # Campo virtual que não existe no modelo
            'telefone',
            'endereco',
            'bairro',
            'cep',
            'cidade',
            'estado',
            'preferred_categories',
            'foto',
        ]
        widgets = {
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua, Número, Complemento'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do bairro'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da cidade'
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SP, RJ, MG...'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'telefone': 'Telefone (Opcional)',
            'endereco': 'Endereço (Opcional)',
            'bairro': 'Bairro (Opcional)',
            'cep': 'CEP (Opcional)',
            'cidade': 'Cidade (Opcional)',
            'estado': 'Estado (Opcional)',
            'foto': 'Foto de Perfil (Opcional)',
            'preferred_categories': 'Categorias de Interesse (Opcional)',
        }
        help_texts = {
            'preferred_categories': 'Escolha até 2 categorias do seu interesse',
            'telefone': 'Para contato direto com clientes/fornecedores',
        }

    def clean_preferred_categories(self):
        cats = self.cleaned_data.get('preferred_categories')
        if cats and len(cats) > 2:
            raise forms.ValidationError("Você só pode escolher no máximo 2 categorias.")
        return cats

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Definir is_client e is_supplier baseado na escolha do usuário
        user_type = self.cleaned_data.get('user_type')
        if user_type == 'client':
            user.is_client = True
            user.is_supplier = False
        elif user_type == 'supplier':
            user.is_client = False
            user.is_supplier = True
        elif user_type == 'both':
            user.is_client = True
            user.is_supplier = True
        
        if commit:
            user.save()
            # Salvar as categorias preferidas (many-to-many)
            self.save_m2m()
            
        return user

class CustomUserCreationForm(UserCreationForm):
    """Formulário completo de cadastro (mantido para compatibilidade)"""
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmação de Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            attrs={
                'data-theme': 'light',  # ou 'dark'
                'data-size': 'normal'   # ou 'compact'
            }
        )
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'is_client', 'is_supplier']
        labels = {
            'email': 'E-mail',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'is_client': 'Cliente',
            'is_supplier': 'Fornecedor',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        
        
    def clean_email(self):
        """
        Valida que o e-mail não está sendo usado por outro usuário.
        """
        email = self.cleaned_data.get('email')
        if email:
            # Verificar se já existe um usuário com este e-mail
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "Este e-mail já está sendo usado por outro usuário. "
                    "Tente fazer login ou use outro e-mail."
                )
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem!")
        return password2

    def clean_password1(self):
        """
        Valida a força da senha usando critérios de segurança.
        """
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                validate_password_strength(password1)
            except forms.ValidationError as e:
                # Re-lançar com as mensagens de validação
                raise forms.ValidationError(e.messages)
        return password1
    
class UserUpdateForm(forms.ModelForm):
    # Campo ManyToMany manual, para permitir escolha de múltiplas categorias
    preferred_categories = forms.ModelMultipleChoiceField(
        label="Categorias Preferidas",
        queryset=Categoria.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-select',  
                'size': 5,
                'placeholder': 'Escolha até 2 categorias'              
            }
        ),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'telefone',
            'data_nascimento',
            'endereco',
            'bairro',
            'cep',
            'cidade',
            'estado',
            'cpf',
            'cnpj',
            'preferred_categories',  
            'comprovante_endereco',
            'foto',
            'is_client',
            'is_supplier',
            
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'comprovante_endereco': forms.FileInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'is_client': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_supplier': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'telefone': 'Telefone',
            'data_nascimento': 'Data de Nascimento',
            'endereco': 'Endereço',
            'bairro': 'Bairro',
            'cep': 'CEP',
            'cidade': 'Cidade',
            'estado': 'Estado',
            'cpf': 'CPF',
            'cnpj': 'CNPJ',
            'comprovante_endereco': 'Comprovante de Endereço',
            'foto': 'Foto',
            'is_client': 'Cliente',
            'is_supplier': 'Fornecedor',
            'preferred_categories': 'Categorias Preferidas',
        }
        help_texts = {
            'preferred_categories': 'Escolha até 2 categorias',
        }

    def clean_email(self):
        """
        Valida que o e-mail não está sendo usado por outro usuário.
        Permite que o usuário mantenha seu próprio e-mail.
        """
        email = self.cleaned_data.get('email')
        if email:
            # Verificar se já existe outro usuário com este e-mail
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError(
                    "Este e-mail já está sendo usado por outro usuário. "
                    "Por favor, use um e-mail diferente."
                )
        return email

    def clean_preferred_categories(self):
        """
        Valida que o usuário escolheu no máximo 2 categorias preferidas.
        """
        cats = self.cleaned_data.get('preferred_categories')
        if cats and len(cats) > 2:
            raise forms.ValidationError("Você só pode escolher no máximo 2 categorias.")
        return cats

    def clean_cpf(self):
        """
        Valida o CPF e armazena somente dígitos.
        """
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Chama a função de validação
            cpf_digits = validate_cpf(cpf)
            return cpf_digits
        return cpf

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajustar o campo 'email' para vir com a classe do Bootstrap
        self.fields['email'].widget = forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu e-mail'
            }
        )

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        # Adicionar atributos de classe e placeholders
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nova senha'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })

    def clean_new_password1(self):
        """
        Valida a força da nova senha usando critérios de segurança.
        """
        password1 = self.cleaned_data.get('new_password1')
        if password1:
            try:
                validate_password_strength(password1)
            except forms.ValidationError as e:
                # Re-lançar com as mensagens de validação
                raise forms.ValidationError(e.messages)
        return password1

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha atual'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nova senha'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })

    def clean_new_password1(self):
        """
        Valida a força da nova senha usando critérios de segurança.
        """
        password1 = self.cleaned_data.get('new_password1')
        if password1:
            try:
                validate_password_strength(password1)
            except forms.ValidationError as e:
                # Re-lançar com as mensagens de validação
                raise forms.ValidationError(e.messages)
        return password1