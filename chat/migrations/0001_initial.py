# Generated manually for chat app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ads', '0001_initial'),
        ('budgets', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('ativo', models.BooleanField(default=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_rooms_as_cliente', to=settings.AUTH_USER_MODEL, verbose_name='Cliente')),
                ('fornecedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_rooms_as_fornecedor', to=settings.AUTH_USER_MODEL, verbose_name='Fornecedor')),
                ('necessidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_rooms', to='ads.necessidade', verbose_name='Necessidade')),
                ('orcamento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='budgets.orcamento', verbose_name='Orçamento Relacionado')),
            ],
            options={
                'verbose_name': 'Sala de Chat',
                'verbose_name_plural': 'Salas de Chat',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conteudo', models.TextField(verbose_name='Conteúdo')),
                ('data_envio', models.DateTimeField(auto_now_add=True)),
                ('lida', models.BooleanField(default=False)),
                ('editada', models.BooleanField(default=False)),
                ('data_edicao', models.DateTimeField(blank=True, null=True)),
                ('arquivo_anexo', models.FileField(blank=True, help_text='Anexar arquivo (máximo 5MB)', null=True, upload_to='chat_anexos/%Y/%m/%d/')),
                ('tipo_arquivo', models.CharField(blank=True, choices=[('imagem', 'Imagem'), ('documento', 'Documento'), ('outros', 'Outros')], max_length=20)),
                ('chat_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensagens', to='chat.chatroom')),
                ('remetente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Remetente')),
            ],
            options={
                'verbose_name': 'Mensagem',
                'verbose_name_plural': 'Mensagens',
                'ordering': ['data_envio'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='chatroom',
            unique_together={('necessidade', 'cliente', 'fornecedor')},
        ),
    ] 