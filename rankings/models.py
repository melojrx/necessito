from django.db import models
from users.models import User  
from ads.models import Necessidade  

class Avaliacao(models.Model):
    """Registra avaliações de fornecedores e clientes"""

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_feitas')  
    avaliado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_recebidas')  
    anuncio = models.ForeignKey(Necessidade, on_delete=models.CASCADE, related_name='avaliacoes')

    TIPO_AVALIACAO_CHOICES = [
        ('fornecedor', 'Fornecedor'),
        ('cliente', 'Cliente'),
        ('negociacao', 'Negociação')
    ]
    
    tipo_avaliacao = models.CharField(max_length=20, choices=TIPO_AVALIACAO_CHOICES)
    estrelas = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5) 
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'avaliado', 'anuncio', 'tipo_avaliacao')  # Garante que cada avaliação seja única

    def __str__(self):
        return f"{self.usuario.get_full_name()} avaliou {self.avaliado.get_full_name()} como {self.tipo_avaliacao} - {self.estrelas} estrelas"
