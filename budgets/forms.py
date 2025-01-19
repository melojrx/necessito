from django import forms
from .models import Orcamento

class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = [
            'descricao', 'quantidade', 'unidade', 'marca',
            'valor', 'prazo_validade', 'prazo_entrega', 'arquivo_anexo', 'observacao'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidade': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'prazo_validade': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prazo_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'arquivo_anexo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'descricao': 'Descrição',
            'quantidade': 'Quantidade',
            'unidade': 'Unidade',
            'marca': 'Marca',
            'valor': 'Valor do Orçamento',
            'prazo_validade': 'Prazo de Validade',
            'prazo_entrega': 'Prazo de Entrega',
            'arquivo_anexo': 'Anexar Arquivo (opcional)',
            'observacao': 'Observações',
        }
