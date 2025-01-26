from django.db import models
from users.models import User
from ads.models import Necessidade

class Orcamento(models.Model):
    fornecedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orcamentos")
    anuncio = models.ForeignKey(Necessidade, on_delete=models.CASCADE, related_name="orcamentos")

    # Replicação dos campos do anúncio
    descricao = models.TextField(blank="True")
    quantidade = models.FloatField()
    unidade = models.CharField(max_length=50)
    marca = models.CharField(max_length=100, blank=True)

    # Campos específicos do orçamento
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    prazo_validade = models.DateField()
    prazo_entrega = models.DateField()
    arquivo_anexo = models.FileField(upload_to='orcamentos_anexos/', blank=True, null=True)
    observacao = models.TextField(blank=True, help_text="Comentários adicionais sobre o orçamento")

    # Status e rastreamento
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('rejeitado', 'Rejeitado'),
    ], default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(blank=True, null=True, auto_now=True)

    def __str__(self):
        return f"Orçamento de {self.fornecedor.get_full_name()} para {self.anuncio.titulo}"
