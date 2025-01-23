from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
import os
from django.conf import settings


def validar_imagem(imagem):
    if not imagem.name.endswith(('.png', '.jpg', '.jpeg')):
        raise ValidationError("Apenas imagens PNG, JPG e JPEG são permitidas.")

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    imagem_local = models.ImageField(
        upload_to='categorias/',
        blank=True,
        null=True,
        help_text="Imagem carregada localmente",
        validators=[validar_imagem]
    )
    url_imagem_externa = models.URLField(
        blank=True,
        null=True,
        help_text="URL de uma imagem externa"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def imagem(self):
        """
        Retorna a imagem local, se existir, caso contrário, a URL externa.
        """
        if self.imagem_local:
            return self.imagem_local.url
        elif self.url_imagem_externa:
            return self.url_imagem_externa
        return None

    def save(self, *args, **kwargs):
        """
        Redimensiona a imagem local antes de salvar e garante que o diretório de mídia exista.
        """
        # Garantir que o diretório de upload existe
        media_path = os.path.join(settings.MEDIA_ROOT, 'categorias')
        os.makedirs(media_path, exist_ok=True)

        # Salvar inicialmente para acessar o arquivo de imagem
        super().save(*args, **kwargs)

        if self.imagem_local:
            # Abrir a imagem carregada
            img = Image.open(self.imagem_local)
            
            # Verificar se a imagem precisa ser redimensionada
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                
                # Salvar a imagem redimensionada no campo imagem_local
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)  # Compressão com qualidade 85
                buffer.seek(0)

                # Atualizar o arquivo da imagem
                self.imagem_local.save(
                    self.imagem_local.name,
                    ContentFile(buffer.read()),
                    save=False  # Não chame o save do modelo novamente
                )


class SubCategoria(models.Model):
    """
    SubCategoria vinculada à Categoria principal.
    """
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='subcategorias'
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} (Categoria: {self.categoria.nome})"
