from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Avaliacao
from budgets.models import Orcamento  # Importando corretamente

class AvaliacaoForm(forms.ModelForm):
    """Formulário para avaliação de fornecedor, cliente ou negociação"""

    estrelas = forms.IntegerField(
        required=True,
        widget=forms.Select(
            choices=[(i, f"{i} ⭐") for i in range(1, 6)],
            attrs={'class': 'form-select form-select-sm d-inline-block', 'style': 'width: auto;'}
        ),
        validators=[
            MinValueValidator(1, 'A avaliação não pode ser INFERIOR a 1 estrela'),
            MaxValueValidator(5, 'A avaliação não pode ser SUPERIOR a 5 estrelas')
        ]
    )

    class Meta:
        model = Avaliacao
        fields = ['estrelas']

    def __init__(self, *args, **kwargs):
        """Filtra as opções disponíveis no campo tipo_avaliacao com base no usuário e no contexto"""
        self.user = kwargs.pop('user', None)
        self.anuncio = kwargs.pop('anuncio', None)
        super(AvaliacaoForm, self).__init__(*args, **kwargs)

        # 🔹 Correção: Buscar o fornecedor do anúncio corretamente
        self.fornecedor = None
        if self.anuncio:
            orcamento_aceito = Orcamento.objects.filter(anuncio=self.anuncio, status='aceito').first()
            self.fornecedor = orcamento_aceito.fornecedor if orcamento_aceito else None

    def clean(self):
        """Validações personalizadas para garantir consistência"""
        cleaned_data = super().clean()
        estrelas = cleaned_data.get('estrelas')

        # Garantir que as estrelas estejam dentro do intervalo permitido
        if estrelas and (estrelas < 1 or estrelas > 5):
            self.add_error('estrelas', 'As estrelas devem estar entre 1 e 5.')

        return cleaned_data
