from django import forms
from django.forms import inlineformset_factory
from .models import Orcamento, OrcamentoItem
from django.utils import timezone

class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = [
            'prazo_validade', 'prazo_entrega', 'arquivo_anexo', 'observacao',
            'tipo_frete', 'valor_frete', 'forma_pagamento', 'condicao_pagamento',
            'condicao_pagamento_personalizada', 'tipo_venda'
        ]
        widgets = {
            'prazo_validade': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'prazo_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'observacao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'arquivo_anexo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'tipo_frete': forms.Select(attrs={'class': 'form-control'}),
            'valor_frete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'condicao_pagamento': forms.Select(attrs={'class': 'form-control', 'id': 'id_condicao_pagamento'}),
            'condicao_pagamento_personalizada': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'id': 'id_condicao_personalizada'}),
            'tipo_venda': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'prazo_validade': 'Prazo de Validade',
            'prazo_entrega': 'Prazo de Entrega',
            'arquivo_anexo': 'Anexar Arquivo (opcional)',
            'observacao': 'Observações',
            'tipo_frete': 'Tipo de Frete',
            'valor_frete': 'Valor do Frete (R$)',
            'forma_pagamento': 'Forma de Pagamento',
            'condicao_pagamento': 'Condição de Pagamento',
            'condicao_pagamento_personalizada': 'Condição Personalizada',
            'tipo_venda': 'Tipo de Venda',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar formato de data para HTML5 date inputs
        self.fields['prazo_validade'].input_formats = ['%Y-%m-%d']
        self.fields['prazo_entrega'].input_formats = ['%Y-%m-%d']

        # Definir data mínima (hoje) nos widgets para bloquear datas passadas no front-end
        today_str = timezone.now().date().isoformat()
        self.fields['prazo_validade'].widget.attrs['min'] = today_str
        self.fields['prazo_entrega'].widget.attrs['min'] = today_str
        
        # Tornar campo personalizado não obrigatório por padrão
        self.fields['condicao_pagamento_personalizada'].required = False
        self.fields['valor_frete'].required = False

    # =====================
    # Validações de data
    # =====================
    def clean_prazo_validade(self):
        prazo_validade = self.cleaned_data.get('prazo_validade')
        if prazo_validade and prazo_validade < timezone.now().date():
            raise forms.ValidationError('O prazo de validade não pode ser anterior à data atual.')
        return prazo_validade

    def clean_prazo_entrega(self):
        prazo_entrega = self.cleaned_data.get('prazo_entrega')
        if prazo_entrega and prazo_entrega < timezone.now().date():
            raise forms.ValidationError('O prazo de entrega não pode ser anterior à data atual.')
        return prazo_entrega

class OrcamentoItemForm(forms.ModelForm):
    class Meta:
        model = OrcamentoItem
        exclude = ('orcamento',)
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control tipo-select'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'unidade': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            
            # Campos de material
            'ncm': forms.TextInput(attrs={'class': 'form-control campo-material'}),
            'icms_percentual': forms.NumberInput(attrs={'class': 'form-control campo-material', 'step': '0.01'}),
            'ipi_percentual': forms.NumberInput(attrs={'class': 'form-control campo-material', 'step': '0.01'}),
            'st_percentual': forms.NumberInput(attrs={'class': 'form-control campo-material', 'step': '0.01'}),
            'difal_percentual': forms.NumberInput(attrs={'class': 'form-control campo-material', 'step': '0.01'}),
            
            # Campos de serviço
            'cnae': forms.TextInput(attrs={'class': 'form-control campo-servico'}),
            'aliquota_iss': forms.NumberInput(attrs={'class': 'form-control campo-servico', 'step': '0.01'}),
        }
        labels = {
            'tipo': 'Tipo',
            'descricao': 'Descrição',
            'quantidade': 'Quantidade',
            'unidade': 'Unidade',
            'valor_unitario': 'Valor Unitário (R$)',
            'ncm': 'NCM',
            'icms_percentual': 'ICMS (%)',
            'ipi_percentual': 'IPI (%)',
            'st_percentual': 'ST (%)',
            'difal_percentual': 'DIFAL (%)',
            'cnae': 'CNAE',
            'aliquota_iss': 'ISS (%)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Obter o tipo do item para mostrar/ocultar campos
        tipo = None
        if self.instance and self.instance.pk:
            tipo = self.instance.tipo
        elif self.data:
            tipo = self.data.get(f'{self.prefix}-tipo', '')
        elif self.initial:
            tipo = self.initial.get('tipo', '')
        
        # Configurar visibilidade dos campos baseado no tipo
        mat_fields = ['ncm', 'icms_percentual', 'ipi_percentual', 'st_percentual', 'difal_percentual']
        srv_fields = ['cnae', 'aliquota_iss']
        
        if tipo == OrcamentoItem.SERVICO:
            # Ocultar campos de material
            for field in mat_fields:
                self.fields[field].widget = forms.HiddenInput()
                self.fields[field].required = False
            # Tornar CNAE obrigatório para serviços
            self.fields['cnae'].required = True
        elif tipo == OrcamentoItem.MATERIAL:
            # Ocultar campos de serviço
            for field in srv_fields:
                self.fields[field].widget = forms.HiddenInput()
                self.fields[field].required = False
            # Tornar NCM obrigatório para materiais
            self.fields['ncm'].required = True
        else:
            # Se não há tipo definido, mostrar todos os campos mas não tornar nenhum obrigatório
            pass

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        
        if tipo == OrcamentoItem.MATERIAL:
            if not cleaned_data.get('ncm'):
                raise forms.ValidationError("NCM é obrigatório para materiais.")
        elif tipo == OrcamentoItem.SERVICO:
            if not cleaned_data.get('cnae'):
                raise forms.ValidationError("CNAE é obrigatório para serviços.")
        
        return cleaned_data

# Inline FormSet para os itens do orçamento
ItemFormSet = inlineformset_factory(
    Orcamento, OrcamentoItem,
    form=OrcamentoItemForm,
    extra=1,  # Começa com 1 item vazio
    can_delete=True,
    min_num=1,  # Mínimo de 1 item
    validate_min=True,
)
