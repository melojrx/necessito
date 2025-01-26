from django.db import models
from django.urls import reverse
from users.models import User
from categories.models import Categoria, SubCategoria

class Necessidade(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="necessidades")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="necessidades")
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, related_name="necessidades")
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    quantidade = models.FloatField()
    medir_no_local = models.BooleanField(default=False)
    unidade = models.CharField(max_length=50, help_text="Ex.: m², unidades, kg")
    marca = models.CharField(max_length=100, blank=True)
    tipo = models.CharField(max_length=100, blank=True)
    bitola = models.IntegerField(blank=True, default=0.0, help_text="Ex.: Milímetros")
    compr = models.IntegerField(blank=True, default=0.0, help_text="Ex.: Metros")
    peso = models.IntegerField(blank=True, default=0.0, help_text="Ex.: Kilogramas")
    altura = models.FloatField(blank=True, default=0.0, help_text="Ex.: Metros")
    status = models.CharField(max_length=20, choices=[
        ('ativo', 'Ativo'),
        ('em_andamento', 'Em andamento'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ], default='ativo')
    ip_usuario = models.GenericIPAddressField(blank=True, null=True, help_text="Endereço IP do usuário que cadastrou o anúncio")
    duracao = models.CharField(max_length=20, blank=True, null=True, help_text="Duração do serviço ou entrega (ex.: 7 dias, 3 horas)")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('necessidade_detail', args=[str(self.pk)])

    def __str__(self):
        return self.titulo
