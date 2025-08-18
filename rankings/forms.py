from django.forms.widgets import RadioSelect
from django.utils.safestring import mark_safe
from django import forms
from django.core.exceptions import ValidationError
from .models import Avaliacao
import logging

logger = logging.getLogger(__name__)

class StarRadioWidget(RadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        # Renderiza inputs radio tradicionais + estrelas clicáveis separadas
        radio_inputs = []
        star_labels = []
        
        for i in range(1, 6):
            is_checked = str(value) == str(i) if value else False
            checked_attr = 'checked' if is_checked else ''
            
            # Input radio oculto tradicional
            radio_inputs.append(f'''
                <input type="radio" name="{name}" value="{i}" {checked_attr} id="{name}_{i}" style="display: none;">
            ''')
            
            # Label clicável para cada estrela
            star_labels.append(f'''
                <span class="star-label" data-rating="{i}" data-field="{name}" title="{i} estrela{'s' if i > 1 else ''}">
                    ★
                </span>
            ''')
        
        return mark_safe(f'''
            <div class="star-rating-container" data-field="{name}">
                {"".join(radio_inputs)}
                <div class="star-display" style="display: flex; justify-content: center; gap: 8px; font-size: 30px; margin: 10px 0;">
                    {"".join(star_labels)}
                </div>
            </div>
        ''')

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = []

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.anuncio = kwargs.pop('anuncio', None)
        self.tipo_avaliacao = kwargs.pop('tipo_avaliacao', None)
        
        logger.info(f"Inicializando formulário para tipo: {self.tipo_avaliacao}")
        
        super().__init__(*args, **kwargs)
        self.add_criterio_fields()
        
        logger.info(f"Formulário inicializado com campos: {list(self.fields.keys())}")
        
        # Adiciona CSS e JS inline para garantir funcionamento
        self.media_css = '''
        <style>
        .star-label {
            color: #ddd;
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }
        .star-label:hover,
        .star-label.filled {
            color: #ffc107;
            transform: scale(1.1);
        }
        </style>
        '''

    def add_criterio_fields(self):
        criterios = self._get_criterios_para_tipo()
        logger.info(f"Adicionando campos para critérios: {criterios}")

        for criterio_key, criterio_label in criterios:
            field_name = f'criterio_{criterio_key}'
            logger.info(f"Adicionando campo: {field_name}")
            
            self.fields[field_name] = forms.ChoiceField(
                label=criterio_label,
                choices=[(i, str(i)) for i in range(1, 6)],
                widget=StarRadioWidget(),
                required=True,
                initial=None,
                error_messages={
                    'required': f'Por favor, avalie o critério "{criterio_label}".',
                    'invalid_choice': 'Selecione uma avaliação válida de 1 a 5 estrelas.'
                }
            )
            
    def get_media_css(self):
        """Retorna CSS necessário para o funcionamento das estrelas"""
        return self.media_css if hasattr(self, 'media_css') else ''
    
    def clean(self):
        cleaned_data = super().clean()
        logger.info(f"Validando formulário. Dados limpos: {cleaned_data}")
        
        # Validar que todos os critérios necessários foram preenchidos
        criterios_necessarios = self._get_criterios_para_tipo()
        missing_criterios = []
        
        for criterio_key, criterio_label in criterios_necessarios:
            field_name = f'criterio_{criterio_key}'
            value = cleaned_data.get(field_name)
            logger.info(f"Validando {field_name}: {value}")
            
            if not value or value == '':
                missing_criterios.append(criterio_label)
                logger.warning(f"Critério obrigatório não preenchido: {field_name}")
        
        if missing_criterios:
            error_msg = f'Os seguintes critérios são obrigatórios: {", ".join(missing_criterios)}'
            logger.error(f"Validação falhou: {error_msg}")
            raise ValidationError(error_msg)
        
        logger.info("Formulário validado com sucesso")
        return cleaned_data
    
    def render_with_media(self):
        """Renderiza o formulário com CSS e JS inline"""
        return self.get_media_css() + str(self) + self.get_media_js()
        
    def _get_criterios_para_tipo(self):
        """Retorna os critérios necessários baseado no tipo de avaliação"""
        if self.tipo_avaliacao == 'cliente':
            return [
                ('rapidez_respostas', 'Rapidez nas respostas'),
                ('pagamento_acordado', 'Pagamento conforme acordado'),
                ('urbanidade_negociacao', 'Urbanidade na negociação'),
            ]
        elif self.tipo_avaliacao == 'fornecedor':
            return [
                ('qualidade_produto', 'Qualidade do Produto'),
                ('pontualidade_entrega', 'Pontualidade na entrega'),
                ('atendimento', 'Atendimento'),
                ('precos_mercado', 'Preços praticados de acordo com o Mercado'),
            ]
        return []
        
    def get_media_js(self):
        """Retorna JavaScript necessário para o funcionamento das estrelas"""
        return '''
        <script>
        // Sistema de estrelas ultraminimalista e robusto
        function initStarsUltraRobust() {
            console.log('🌟 Inicializando sistema ultra-robusto de estrelas');
            
            // Remove listeners anteriores
            document.removeEventListener('click', starClickHandler);
            document.addEventListener('click', starClickHandler);
            
            // Handler unificado para cliques
            function starClickHandler(event) {
                if (!event.target.classList.contains('star-label')) return;
                
                const star = event.target;
                const rating = parseInt(star.getAttribute('data-rating'));
                const fieldName = star.getAttribute('data-field');
                
                if (!rating || !fieldName) return;
                
                console.log(`Clique na estrela ${rating} do campo ${fieldName}`);
                
                // Marca o input correspondente
                const input = document.getElementById(`${fieldName}_${rating}`);
                if (input) {
                    input.checked = true;
                    console.log(`Input ${fieldName}_${rating} marcado`);
                }
                
                // Atualiza visual das estrelas
                const container = star.closest('.star-rating-container');
                if (container) {
                    const allStars = container.querySelectorAll('.star-label');
                    allStars.forEach((s, index) => {
                        if (index < rating) {
                            s.classList.add('filled');
                        } else {
                            s.classList.remove('filled');
                        }
                    });
                }
            }
            
            // Inicializa estado visual
            document.querySelectorAll('.star-rating-container').forEach(container => {
                const fieldName = container.getAttribute('data-field');
                const checkedInput = container.querySelector('input:checked');
                if (checkedInput) {
                    const rating = parseInt(checkedInput.value);
                    const stars = container.querySelectorAll('.star-label');
                    stars.forEach((s, index) => {
                        if (index < rating) {
                            s.classList.add('filled');
                        }
                    });
                }
            });
            
            console.log('✅ Sistema de estrelas ultra-robusto inicializado');
        }
        
        // Exporta globalmente
        window.initStarsUltraRobust = initStarsUltraRobust;
        
        // Auto-inicialização
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initStarsUltraRobust);
        } else {
            initStarsUltraRobust();
        }
        </script>
        '''
    