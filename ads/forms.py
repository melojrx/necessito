from django import forms
from ads.models import Necessidade
from categories.models import Categoria, SubCategoria

class AdsForms(forms.ModelForm):
    class Meta:
        model = Necessidade
        fields = [
            'categoria',
            'subcategoria',
            'titulo',
            'descricao',
            'quantidade',
            'medir_no_local',
            'unidade',
            'marca',
            'tipo',
            'bitola',
            'compr',
            'peso',
            'altura',
            'status',
        ]
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'subcategoria': forms.Select(attrs={'class': 'form-control'}),

            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),

            'medir_no_local': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            'unidade': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'bitola': forms.NumberInput(attrs={'class': 'form-control'}),
            'compr': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control'}),

            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'categoria': 'Categoria',
            'subcategoria': 'Subcategoria',
            'titulo': 'Título',
            'descricao': 'Descrição',
            'quantidade': 'Quantidade',
            'medir_no_local': 'Medir no Local',
            'unidade': 'Unidade',
            'marca': 'Marca',
            'tipo': 'Tipo',
            'bitola': 'Bitola (mm)',
            'compr': 'Comprimento (m)',
            'peso': 'Peso (Kg)',
            'altura': 'Altura (m)',
            'status': 'Status',
        }
        help_texts = {
            'unidade': 'Ex.: m², unidades, kg',
            'bitola': 'Em milímetros (mm)',
            'compr': 'Em metros (m)',
            'peso': 'Em quilogramas (Kg)',
            'altura': 'Em metros (m)',
        }
