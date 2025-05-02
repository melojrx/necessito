from django.forms.widgets import RadioSelect
from django.utils.safestring import mark_safe
from django import forms
from .models import Avaliacao

class StarRadioWidget(RadioSelect):
    template_name = 'widgets/star_radio_widget.html'

    def render(self, name, value, attrs=None, renderer=None):
        output = []
        for i in reversed(range(1, 6)):
            checked = 'checked' if str(value) == str(i) else ''
            output.append(f'''
                <input id="star{i}_{name}" type="radio" name="{name}" value="{i}" {checked}/>
                <label for="star{i}_{name}"></label>
            ''')
        return mark_safe(f'<div class="star-rating">{"".join(output)}</div>')

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
                choices=[(i, "") for i in range(1, 6)],
                widget=StarRadioWidget(),  # Usa o widget personalizado aqui
                required=True,
                initial=5
            )
    
    