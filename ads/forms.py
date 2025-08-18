from django import forms
from django.forms import ValidationError
from django.utils import timezone
from .models import Necessidade, Disputa
from core.services.address_service import BrazilianStates

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
    
    def clean_data_validade(self):
        data_validade = self.cleaned_data.get('data_validade')
        
        if data_validade:
            # Verificar se a data é no futuro
            if data_validade <= timezone.now():
                raise ValidationError("A data de validade deve ser no futuro.")
            
            # Verificar se não é muito distante (máximo 1 ano)
            max_data = timezone.now() + timezone.timedelta(days=365)
            if data_validade > max_data:
                raise ValidationError("A data de validade não pode ser superior a 1 ano.")
        
        return data_validade
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-preencher campos de endereço com dados do usuário se for novo
        if self.user and not self.instance.pk:
            self.fields['cidade_servico'].initial = self.user.cidade or ''
            self.fields['estado_servico'].initial = self.user.estado or ''
            self.fields['cep_servico'].initial = self.user.cep or ''
            self.fields['bairro_servico'].initial = self.user.bairro or ''
            self.fields['endereco_servico'].initial = self.user.endereco or ''
    
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
            'data_validade',
            
            # ==================== CAMPOS DE ENDEREÇO ====================
            'usar_endereco_usuario',
            'cep_servico',
            'endereco_servico',
            'numero_servico',
            'complemento_servico',
            'bairro_servico',
            'cidade_servico',
            'estado_servico',
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
            'data_validade': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'title': 'Data e hora em que o anúncio expirará automaticamente'
            }),
            
            # ==================== WIDGETS DE ENDEREÇO ====================
            'usar_endereco_usuario': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'useUserAddress',
                'checked': True
            }),
            'cep_servico': forms.TextInput(attrs={
                'class': 'form-control endereco-field',
                'placeholder': '12345-678',
                'maxlength': '10',
                'data-mask': '00000-000'
            }),
            'endereco_servico': forms.TextInput(attrs={
                'class': 'form-control endereco-field address-autocomplete',
                'placeholder': 'Ex: Rua das Flores'
            }),
            'numero_servico': forms.TextInput(attrs={
                'class': 'form-control endereco-field',
                'placeholder': '123'
            }),
            'complemento_servico': forms.TextInput(attrs={
                'class': 'form-control endereco-field',
                'placeholder': 'Apt 45, Bloco B'
            }),
            'bairro_servico': forms.TextInput(attrs={
                'class': 'form-control endereco-field',
                'placeholder': 'Ex: Centro'
            }),
            'cidade_servico': forms.TextInput(attrs={
                'class': 'form-control endereco-field',
                'placeholder': 'Ex: São Paulo'
            }),
            'estado_servico': forms.Select(
                choices=BrazilianStates.get_choices(),
                attrs={'class': 'form-control endereco-field'}
            ),
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
            'data_validade': 'Data de Validade',
            
            # ==================== LABELS DE ENDEREÇO ====================
            'usar_endereco_usuario': 'Usar meu endereço cadastrado',
            'cep_servico': 'CEP do local do serviço',
            'endereco_servico': 'Endereço (Rua/Avenida)',
            'numero_servico': 'Número',
            'complemento_servico': 'Complemento',
            'bairro_servico': 'Bairro',
            'cidade_servico': 'Cidade',
            'estado_servico': 'Estado',
        }
        help_texts = {
            'unidade': 'Ex.: m², unidades, kg',
            'bitola': 'Em milímetros (mm)',
            'compr': 'Ex: metros (m)',
            'peso': 'Ex: quilogramas (Kg)',
            'altura': 'Ex: metros (m)',
            'duracao': 'Informe a duração (Ex.: 7 dias, 3:00:00)',
            'data_validade': 'Data e hora em que o anúncio expirará automaticamente. Se não informado, será definido para 30 dias após a criação.',
            
            # ==================== HELP TEXTS DE ENDEREÇO ====================
            'usar_endereco_usuario': 'Marque se o serviço será executado no seu endereço cadastrado',
            'cep_servico': 'Digite o CEP para preenchimento automático',
            'endereco_servico': 'O endereço será preenchido automaticamente pelo CEP',
            'numero_servico': 'Número do local onde será executado o serviço',
            'complemento_servico': 'Apartamento, sala, bloco, etc. (opcional)',
            'cidade_servico': 'Cidade onde o serviço será executado',
            'estado_servico': 'Estado onde o serviço será executado',
        }


class DisputaForm(forms.ModelForm):
    """Formulário para abertura de disputas."""
    
    class Meta:
        model = Disputa
        fields = ['motivo', 'arquivo_evidencia']
        
        widgets = {
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Descreva detalhadamente o problema ou conflito...',
                'required': True
            }),
            'arquivo_evidencia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt'
            })
        }
        
        labels = {
            'motivo': 'Motivo da Disputa',
            'arquivo_evidencia': 'Arquivo de Evidência (opcional)',
        }
        
        help_texts = {
            'motivo': 'Explique claramente o problema, incluindo datas, valores e situações relevantes.',
            'arquivo_evidencia': 'Anexe documentos, fotos ou outros arquivos que comprovem sua alegação (máx. 10MB).',
        }
    
    def clean_motivo(self):
        """Validar motivo da disputa."""
        motivo = self.cleaned_data.get('motivo', '').strip()
        
        if not motivo:
            raise ValidationError('O motivo da disputa é obrigatório.')
        
        if len(motivo) < 50:
            raise ValidationError('O motivo deve ter pelo menos 50 caracteres para uma descrição adequada.')
        
        if len(motivo) > 2000:
            raise ValidationError('O motivo não pode exceder 2000 caracteres.')
        
        return motivo
    
    def clean_arquivo_evidencia(self):
        """Validar arquivo de evidência."""
        arquivo = self.cleaned_data.get('arquivo_evidencia')
        
        if not arquivo:
            return arquivo
        
        # Validar tamanho (máximo 10MB)
        if arquivo.size > 10 * 1024 * 1024:
            raise ValidationError('O arquivo não pode exceder 10MB.')
        
        # Validar tipos de arquivo permitidos
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/png',
            'text/plain'
        ]
        
        if arquivo.content_type not in allowed_types:
            raise ValidationError(
                'Tipo de arquivo não permitido. '
                'Use: PDF, Word, JPEG, PNG ou TXT.'
            )
        
        return arquivo


class DisputaResolverForm(forms.ModelForm):
    """Formulário para administradores resolverem disputas."""
    
    class Meta:
        model = Disputa
        fields = ['status', 'resolucao', 'status_final_necessidade', 'comentarios_internos']
        
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'resolucao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Descreva a resolução da disputa...'
            }),
            'status_final_necessidade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comentarios_internos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Comentários visíveis apenas para administradores...'
            })
        }
        
        labels = {
            'status': 'Status da Disputa',
            'resolucao': 'Resolução',
            'status_final_necessidade': 'Status Final da Necessidade',
            'comentarios_internos': 'Comentários Internos',
        }
        
        help_texts = {
            'status': 'Selecione o novo status da disputa.',
            'resolucao': 'Explicação da resolução que será enviada às partes envolvidas.',
            'status_final_necessidade': 'Para onde a necessidade deve ir após a resolução (obrigatório ao resolver).',
            'comentarios_internos': 'Comentários que ficarão registrados apenas para a equipe administrativa.',
        }
    
    def clean_resolucao(self):
        """Validar resolução."""
        resolucao = self.cleaned_data.get('resolucao', '').strip()
        status = self.cleaned_data.get('status')
        
        if status == 'resolvida' and not resolucao:
            raise ValidationError('A resolução é obrigatória ao resolver uma disputa.')
        
        if resolucao and len(resolucao) < 20:
            raise ValidationError('A resolução deve ter pelo menos 20 caracteres.')
        
        return resolucao
    
    def clean_status_final_necessidade(self):
        """Validar status final da necessidade."""
        status_final = self.cleaned_data.get('status_final_necessidade')
        status = self.cleaned_data.get('status')
        
        if status == 'resolvida' and not status_final:
            raise ValidationError('Status final da necessidade é obrigatório ao resolver disputa.')
        
        return status_final
    
    def clean(self):
        """Validação geral do formulário."""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        resolucao = cleaned_data.get('resolucao')
        status_final = cleaned_data.get('status_final_necessidade')
        
        # Validações cruzadas para status resolvida
        if status == 'resolvida':
            if not resolucao:
                self.add_error('resolucao', 'Resolução é obrigatória.')
            if not status_final:
                self.add_error('status_final_necessidade', 'Status final é obrigatório.')
        
        return cleaned_data


class DisputaFiltroForm(forms.Form):
    """Formulário para filtrar disputas na listagem."""
    
    STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('aberta', 'Aberta'),
        ('em_analise', 'Em análise'),
        ('resolvida', 'Resolvida'),
        ('cancelada', 'Cancelada'),
    ]
    
    PERIODO_CHOICES = [
        ('', 'Todo o período'),
        ('hoje', 'Hoje'),
        ('semana', 'Esta semana'),
        ('mes', 'Este mês'),
        ('trimestre', 'Este trimestre'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por necessidade, usuário...'
        })
    )
    
    urgente_apenas = forms.BooleanField(
        required=False,
        label='Apenas disputas urgentes (>48h)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
