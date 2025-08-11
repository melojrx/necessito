import json
import subprocess
import threading
import time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.management import call_command
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import logging

from core.mixins import AdminRequiredMixin
from categories.models import Categoria, SubCategoria
from users.models import User

logger = logging.getLogger(__name__)

# Dicionário para armazenar o progresso dos comandos
command_progress = {}

class AdminPanelView(AdminRequiredMixin, TemplateView):
    """View principal da área administrativa"""
    template_name = 'admin_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas do sistema
        context.update({
            'total_categorias': Categoria.objects.count(),
            'total_subcategorias': SubCategoria.objects.count(),
            'total_usuarios': User.objects.count(),
            'usuarios_sem_geolocalizacao': User.objects.filter(
                lat__isnull=True, lon__isnull=True
            ).exclude(cidade='').exclude(estado='').count(),
            'usuarios_com_cep_sem_geo': User.objects.filter(
                cep__isnull=False, lat__isnull=True, lon__isnull=True
            ).exclude(cep='').count(),
        })
        
        return context

class ImportCategoriesView(AdminRequiredMixin, TemplateView):
    """View para importar categorias e subcategorias"""
    template_name = 'admin_panel/import_categories.html'
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
            categorias_file = request.FILES.get('categorias_file')
            subcategorias_file = request.FILES.get('subcategorias_file')
            
            if not categorias_file or not subcategorias_file:
                return JsonResponse({
                    'success': False,
                    'message': 'Ambos os arquivos são obrigatórios'
                })
            
            # Salvar arquivos temporariamente
            cat_path = default_storage.save(
                f'temp/categorias_{int(time.time())}.csv',
                ContentFile(categorias_file.read())
            )
            subcat_path = default_storage.save(
                f'temp/subcategorias_{int(time.time())}.csv',
                ContentFile(subcategorias_file.read())
            )
            
            # Executar comando em thread separada
            command_id = f'import_categories_{int(time.time())}'
            thread = threading.Thread(
                target=self._run_import_command,
                args=(command_id, cat_path, subcat_path)
            )
            thread.start()
            
            return JsonResponse({
                'success': True,
                'command_id': command_id,
                'message': 'Importação iniciada'
            })
            
        except Exception as e:
            logger.error(f'Erro na importação de categorias: {e}')
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    def _run_import_command(self, command_id, cat_path, subcat_path):
        """Executa o comando de importação em background"""
        try:
            command_progress[command_id] = {
                'status': 'running',
                'progress': 0,
                'message': 'Iniciando importação...'
            }
            
            # Converter paths para absolutos
            cat_full_path = os.path.join(settings.MEDIA_ROOT, cat_path)
            subcat_full_path = os.path.join(settings.MEDIA_ROOT, subcat_path)
            
            command_progress[command_id].update({
                'progress': 25,
                'message': 'Importando categorias...'
            })
            
            # Executar comando
            call_command('import_categories', cat_full_path, subcat_full_path)
            
            command_progress[command_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Importação concluída com sucesso!'
            })
            
            # Limpar arquivos temporários
            try:
                os.remove(cat_full_path)
                os.remove(subcat_full_path)
            except:
                pass
                
        except Exception as e:
            command_progress[command_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Erro: {str(e)}'
            }

class UpdateSubcategoryDescriptionsView(AdminRequiredMixin, TemplateView):
    """View para atualizar descrições das subcategorias"""
    template_name = 'admin_panel/update_descriptions.html'
    
    def get_context_data(self, **kwargs):
        from django.db import models
        context = super().get_context_data(**kwargs)
        
        total_subcategorias = SubCategoria.objects.count()
        subcategorias_sem_descricao = SubCategoria.objects.filter(
            models.Q(descricao__isnull=True) | models.Q(descricao__exact='')
        ).count()
        
        context.update({
            'total_subcategorias': total_subcategorias,
            'subcategorias_sem_descricao': subcategorias_sem_descricao,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            command_id = f'update_descriptions_{int(time.time())}'
            thread = threading.Thread(
                target=self._run_update_command,
                args=(command_id,)
            )
            thread.start()
            
            return JsonResponse({
                'success': True,
                'command_id': command_id,
                'message': 'Atualização iniciada'
            })
            
        except Exception as e:
            logger.error(f'Erro na atualização de descrições: {e}')
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    def _run_update_command(self, command_id):
        """Executa o comando de atualização em background"""
        try:
            command_progress[command_id] = {
                'status': 'running',
                'progress': 0,
                'message': 'Iniciando atualização...'
            }
            
            command_progress[command_id].update({
                'progress': 50,
                'message': 'Atualizando descrições das subcategorias...'
            })
            
            call_command('atualizar_descricoes_subcategorias')
            
            command_progress[command_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Descrições atualizadas com sucesso!'
            })
                
        except Exception as e:
            command_progress[command_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Erro: {str(e)}'
            }

class PopulateIconsView(AdminRequiredMixin, TemplateView):
    """View para popular ícones das categorias"""
    template_name = 'admin_panel/populate_icons.html'
    
    def get_context_data(self, **kwargs):
        from django.db import models
        context = super().get_context_data(**kwargs)
        
        total_categorias = Categoria.objects.count()
        categorias_com_icone = Categoria.objects.filter(
            ~models.Q(icone__isnull=True) & ~models.Q(icone__exact='')
        ).count()
        categorias_sem_icone = total_categorias - categorias_com_icone
        
        context.update({
            'total_categorias': total_categorias,
            'categorias_com_icone': categorias_com_icone,
            'categorias_sem_icone': categorias_sem_icone,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            command_id = f'populate_icons_{int(time.time())}'
            thread = threading.Thread(
                target=self._run_icons_command,
                args=(command_id,)
            )
            thread.start()
            
            return JsonResponse({
                'success': True,
                'command_id': command_id,
                'message': 'População de ícones iniciada'
            })
            
        except Exception as e:
            logger.error(f'Erro na população de ícones: {e}')
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    def _run_icons_command(self, command_id):
        """Executa o comando de ícones em background"""
        try:
            command_progress[command_id] = {
                'status': 'running',
                'progress': 0,
                'message': 'Iniciando população de ícones...'
            }
            
            command_progress[command_id].update({
                'progress': 50,
                'message': 'Populando ícones das categorias...'
            })
            
            call_command('popular_icones')
            
            command_progress[command_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Ícones populados com sucesso!'
            })
                
        except Exception as e:
            command_progress[command_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Erro: {str(e)}'
            }

class ImportUsersView(AdminRequiredMixin, TemplateView):
    """View para importar usuários de teste"""
    template_name = 'admin_panel/import_users.html'
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
            users_file = request.FILES.get('users_file')
            
            if not users_file:
                return JsonResponse({
                    'success': False,
                    'message': 'Arquivo de usuários é obrigatório'
                })
            
            # Salvar arquivo temporariamente
            file_path = default_storage.save(
                f'temp/usuarios_{int(time.time())}.json',
                ContentFile(users_file.read())
            )
            
            # Executar comando em thread separada
            command_id = f'import_users_{int(time.time())}'
            thread = threading.Thread(
                target=self._run_import_users_command,
                args=(command_id, file_path)
            )
            thread.start()
            
            return JsonResponse({
                'success': True,
                'command_id': command_id,
                'message': 'Importação de usuários iniciada'
            })
            
        except Exception as e:
            logger.error(f'Erro na importação de usuários: {e}')
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    def _run_import_users_command(self, command_id, file_path):
        """Executa o comando de importação de usuários em background"""
        try:
            command_progress[command_id] = {
                'status': 'running',
                'progress': 0,
                'message': 'Iniciando importação de usuários...'
            }
            
            # Converter path para absoluto
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            command_progress[command_id].update({
                'progress': 50,
                'message': 'Importando usuários...'
            })
            
            # Executar comando
            call_command('importar_usuarios', full_path)
            
            command_progress[command_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Usuários importados com sucesso!'
            })
            
            # Limpar arquivo temporário
            try:
                os.remove(full_path)
            except:
                pass
                
        except Exception as e:
            command_progress[command_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Erro: {str(e)}'
            }

class GeolocalizeUsersView(AdminRequiredMixin, TemplateView):
    """View para geolocalizar usuários"""
    template_name = 'admin_panel/geolocalize_users.html'
    
    def get_context_data(self, **kwargs):
        from django.db import models
        context = super().get_context_data(**kwargs)
        
        total_usuarios = User.objects.count()
        usuarios_sem_geolocalizacao = User.objects.filter(
            lat__isnull=True, lon__isnull=True
        ).exclude(cidade='').exclude(estado='').count()
        usuarios_com_cep_sem_geo = User.objects.filter(
            cep__isnull=False, lat__isnull=True, lon__isnull=True
        ).exclude(cep='').count()
        usuarios_com_geolocalizacao = User.objects.filter(
            lat__isnull=False, lon__isnull=False
        ).count()
        
        context.update({
            'total_usuarios': total_usuarios,
            'usuarios_sem_geolocalizacao': usuarios_sem_geolocalizacao,
            'usuarios_com_cep_sem_geo': usuarios_com_cep_sem_geo,
            'usuarios_com_geolocalizacao': usuarios_com_geolocalizacao,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            command_type = request.POST.get('command_type', 'geolocalizar')
            
            command_id = f'{command_type}_users_{int(time.time())}'
            thread = threading.Thread(
                target=self._run_geo_command,
                args=(command_id, command_type)
            )
            thread.start()
            
            return JsonResponse({
                'success': True,
                'command_id': command_id,
                'message': f'Geolocalização iniciada ({command_type})'
            })
            
        except Exception as e:
            logger.error(f'Erro na geolocalização: {e}')
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    def _run_geo_command(self, command_id, command_type):
        """Executa o comando de geolocalização em background"""
        try:
            command_progress[command_id] = {
                'status': 'running',
                'progress': 0,
                'message': 'Iniciando geolocalização...'
            }
            
            if command_type == 'geolocalizar':
                command_progress[command_id].update({
                    'progress': 25,
                    'message': 'Geolocalizando usuários sem coordenadas...'
                })
                call_command('geolocalizar_usuarios')
            elif command_type == 'atualizar':
                command_progress[command_id].update({
                    'progress': 25,
                    'message': 'Atualizando geolocalização por CEP...'
                })
                call_command('atualizar_geolocalizacao_usuarios')
            
            command_progress[command_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Geolocalização concluída com sucesso!'
            })
                
        except Exception as e:
            command_progress[command_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Erro: {str(e)}'
            }

class UpdateGeolocalizationView(AdminRequiredMixin, TemplateView):
    """View para atualizar geolocalização existente"""
    
    def post(self, request, *args, **kwargs):
        try:
            command_id = f'update_geo_{int(time.time())}'
            thread = threading.Thread(
                target=self._run_update_geo_command,
                args=(command_id,)
            )
            thread.start()
            
            return JsonResponse({
                'success': True,
                'command_id': command_id,
                'message': 'Atualização de geolocalização iniciada'
            })
            
        except Exception as e:
            logger.error(f'Erro na atualização de geolocalização: {e}')
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    def _run_update_geo_command(self, command_id):
        """Executa o comando de atualização de geolocalização em background"""
        try:
            command_progress[command_id] = {
                'status': 'running',
                'progress': 0,
                'message': 'Iniciando atualização de geolocalização...'
            }
            
            command_progress[command_id].update({
                'progress': 50,
                'message': 'Atualizando geolocalização dos usuários...'
            })
            
            call_command('atualizar_geolocalizacao_usuarios')
            
            command_progress[command_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Atualização de geolocalização concluída com sucesso!'
            })
                
        except Exception as e:
            command_progress[command_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Erro: {str(e)}'
            }

@csrf_exempt
def command_progress_api(request, command_id):
    """API para verificar o progresso de um comando"""
    if request.method == 'GET':
        progress_data = command_progress.get(command_id, {
            'status': 'not_found',
            'progress': 0,
            'message': 'Comando não encontrado'
        })
        return JsonResponse(progress_data)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

def clear_command_progress(request, command_id):
    """Limpa o progresso de um comando específico"""
    if command_id in command_progress:
        del command_progress[command_id]
    return JsonResponse({'success': True})