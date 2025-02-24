from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from users.models import User
from categories.models import Categoria

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemplo@necessito.br'
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '********'
        })
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

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmação de Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

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

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem!")
        return password2
    
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
def clean_preferred_categories(self):
    cats = self.cleaned_data.get('preferred_categories')
    if cats and len(cats) > 2:
        raise forms.ValidationError("Você só pode escolher no máximo 2 categorias.")
    return cats

