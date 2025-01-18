from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_client', 'is_supplier', 'is_staff', 'is_superuser')
    list_filter = ('is_client', 'is_supplier', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')  # Campos somente leitura

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'telefone', 'endereco')}),
        ('Permissões', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),  # Campos adicionados aqui como readonly
        ('Tipo de Usuário', {'fields': ('is_client', 'is_supplier')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_client', 'is_supplier', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
