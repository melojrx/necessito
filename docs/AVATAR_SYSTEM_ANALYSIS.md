# 📋 Análise do Sistema de Avatar Padrão vs Foto Real

## 🔍 **Como o Sistema Funciona Atualmente:**

### **1. Modelo User (users/models.py)**
```python
foto = models.ImageField(
    "Foto de perfil",
    upload_to="fotos_usuarios/",
    blank=True,
    null=True,
    help_text="Envie uma imagem quadrada (recomendado 400×400 px)",
)

@property
def foto_url(self) -> str:
    """Retorna URL da foto de perfil ou um avatar padrão."""
    if self.foto:
        return self.foto.url  # Foto real do usuário
    else:
        return f"{settings.STATIC_URL}img/avatar.png"  # Avatar padrão
```

### **2. Templates Atualizados:**
- ✅ `users/templates/minha-conta-detail.html` - Usa `{{ user.foto_url }}`
- ✅ `templates/components/bottom_nav.html` - Corrigido para usar `{{ user.foto_url }}`
- ✅ `users/templates/user_profile.html` - Corrigido para usar `{{ user.foto_url }}`
- ✅ `search/templates/components/_search_results.html` - Corrigido para usar `{{ ad.cliente.foto_url }}`

### **3. Formulário de Upload (users/forms.py)**
```python
class UserUpdateForm(forms.ModelForm):
    fields = ['foto', ...]  # Campo foto incluído
    widgets = {
        'foto': forms.FileInput(attrs={'class': 'form-control'}),
    }
```

### **4. View de Edição (users/views.py)**
```python
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'minha-conta-update.html'
```

### **5. Template de Edição (users/templates/minha-conta-update.html)**
```html
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}  <!-- Inclui campo de upload de foto -->
    <button type="submit" class="btn btn-primary">Salvar Alterações</button>
</form>
```

## 🔄 **Fluxo de Funcionamento:**

### **Cenário 1: Usuário Sem Foto (Avatar Padrão)**
1. `user.foto` = `None` ou campo vazio
2. `user.foto_url` retorna `"/static/img/avatar.png"`
3. Templates mostram avatar azul padrão

### **Cenário 2: Usuário Faz Upload de Foto**
1. Usuário acessa `/users/minha-conta/edit/`
2. Preenche formulário com nova foto
3. Django salva arquivo em `media/fotos_usuarios/`
4. `user.foto` = campo preenchido com caminho do arquivo
5. `user.foto_url` retorna `user.foto.url` (ex: `/media/fotos_usuarios/foto123.jpg`)
6. Templates mostram foto real do usuário

### **Cenário 3: Usuário Remove Foto**
1. Se o campo foto for limpo/removido
2. `user.foto` volta a ser `None`
3. `user.foto_url` volta a retornar avatar padrão
4. Templates automaticamente voltam a mostrar avatar azul

## ✅ **Verificações Realizadas:**

### **Inconsistências Corrigidas:**
- ❌ `bottom_nav.html` usava condições `{% if user.foto %}` → ✅ Agora usa `{{ user.foto_url }}`
- ❌ `user_profile.html` usava condições separadas → ✅ Agora usa `{{ user.foto_url }}`
- ❌ `_search_results.html` usava condições → ✅ Agora usa `{{ ad.cliente.foto_url }}`

### **Sistema Unificado:**
- ✅ Todos os templates agora usam `user.foto_url`
- ✅ Avatar padrão movido de `media/` para `static/img/avatar.png`
- ✅ Lógica centralizada no método `foto_url` do modelo

## 🎯 **Comportamento Esperado:**

1. **Cadastro Inicial:** Usuário aparece com avatar azul padrão
2. **Upload de Foto:** Avatar muda para foto real instantaneamente
3. **Remoção de Foto:** Volta automaticamente para avatar padrão
4. **Navegação:** Avatar consistente em todos os locais (menu, perfil, resultados)

## 🔧 **Próximos Passos:**

1. ✅ Coletar arquivos estáticos (avatar.png disponível)
2. ✅ Testar upload de foto via interface
3. ✅ Verificar se remoção de foto restaura avatar padrão
4. ✅ Validar consistência visual em todos os templates

O sistema está **funcionalmente correto** e **centralizado** no método `foto_url`!
