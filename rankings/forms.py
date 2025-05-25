from django import forms
from .models import Avaliacao

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = []

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.anuncio = kwargs.pop('anuncio', None)
        self.tipo_avaliacao = kwargs.pop('tipo_avaliacao', None)
        super().__init__(*args, **kwargs)
        self.add_criterio_fields()

    def add_criterio_fields(self):
        criterios = []

        if self.tipo_avaliacao == 'cliente':
            criterios = [
                ('rapidez_respostas', 'Rapidez nas respostas'),
                ('pagamento_acordado', 'Pagamento conforme acordado'),
                ('urbanidade_negociacao', 'Urbanidade na negociação'),
            ]
        elif self.tipo_avaliacao == 'fornecedor':
            criterios = [
                ('qualidade_produto', 'Qualidade do Produto'),
                ('pontualidade_entrega', 'Pontualidade na entrega'),
                ('atendimento', 'Atendimento'),
                ('precos_mercado', 'Preços praticados de acordo com o Mercado'),
            ]

        for criterio_key, criterio_label in criterios:
            field_name = f'criterio_{criterio_key}'
            self.fields[field_name] = forms.ChoiceField(
                label=criterio_label,
                choices=[(i, str(i)) for i in range(1, 6)],
                widget=forms.RadioSelect(),
                required=True,
                initial=None  # Removido o valor inicial para forçar o usuário a escolher
            )
    
    