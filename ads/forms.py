from django import forms
from django.forms import ValidationError
from .models import Necessidade

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]
    
class AdsForms(forms.ModelForm):
    imagens = MultipleFileField(
        required=False,
        label='Fotos do Anúncio',  # Alterado para Font Awesome
        help_text='Selecione até 3 imagens (JPEG/PNG, máx. 5MB cada)',
        widget=MultipleFileInput(attrs={
            'class': 'form-control custom-file-input',
            'aria-describedby': 'imagensHelp'
        })
    )    

    def clean_imagens(self):
        imagens = self.cleaned_data.get('imagens', [])
        
        # Validação de quantidade
        if len(imagens) > 3:
            raise ValidationError("Máximo de 3 imagens permitidas!")
        
        # Validação de tipo e tamanho
        valid_types = ['image/jpeg', 'image/png']
        for img in imagens:
            if img.content_type not in valid_types:
                raise ValidationError(f"Formato inválido: {img.name}. Use apenas JPEG ou PNG.")
            if img.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError(f"Imagem {img.name} excede 5MB!")
        
        return imagens
    
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
            'duracao',  
        ]
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'subcategoria': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'medir_no_local': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'bitola': forms.NumberInput(attrs={'class': 'form-control'}),
            'compr': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control'}),
            'duracao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: 7 dias, 3:00:00'
            }), 
             
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
            'duracao': 'Duração', 
        }
        help_texts = {
            'unidade': 'Ex.: m², unidades, kg',
            'bitola': 'Em milímetros (mm)',
            'compr': 'Ex: metros (m)',
            'peso': 'Ex: quilogramas (Kg)',
            'altura': 'Ex: metros (m)',
            'duracao': 'Informe a duração (Ex.: 7 dias, 3:00:00)',  
        }
        
    
