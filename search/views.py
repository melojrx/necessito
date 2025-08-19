from django.views.generic import ListView
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from ads.models import Necessidade, Categoria, AnuncioImagem
from categories.models import SubCategoria
from .security_utils import (
    validate_search_term, validate_location, validate_client_name,
    validate_coordinates, validate_status_list, validate_search_fields,
    rate_limit_decorator, log_suspicious_activity
)
import math
import logging

# Logger para operações de busca
search_logger = logging.getLogger('search.operations')

class NecessidadeSearchAllView(ListView):
    model = Necessidade
    template_name = "results.html"
    context_object_name = "anuncios"
    paginate_by = 20

    def get_queryset(self):
        # Otimizar consulta com apenas os campos necessários
        qs = (
            Necessidade.objects
            .select_related("categoria", "subcategoria", "cliente")
            .prefetch_related(
                Prefetch("imagens", queryset=AnuncioImagem.objects.only('id', 'anuncio_id', 'imagem').order_by("id"))
            )
            .only(
                'id', 'titulo', 'descricao', 'status', 'data_criacao', 'quantidade', 'unidade',
                'categoria__nome', 'categoria__icone',
                'subcategoria__nome',
                'cliente__first_name', 'cliente__last_name', 'cliente__cidade',
                'cliente__bairro', 'cliente__estado'
            )
        )

        # Validação segura de status
        status_raw = self.request.GET.getlist("status")
        self.status_selecionados = validate_status_list(status_raw)
        
        # Aplicar filtro de status
        qs = qs.filter(status__in=self.status_selecionados)

        # Validação segura de estado
        state_raw = self.request.GET.get("state", "todos").strip().upper()
        # Lista de estados válidos do Brasil
        estados_validos = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO', 'TODOS'
        ]
        
        self.state_sigla = state_raw if state_raw in estados_validos else "TODOS"
        if self.state_sigla != "TODOS":
            qs = qs.filter(cliente__estado=self.state_sigla)

        # Validação segura do termo de busca
        term_raw = self.request.GET.get("q", "").strip()
        term_valid, self.term, term_error = validate_search_term(term_raw)
        
        if not term_valid:
            search_logger.warning(f"Invalid search term rejected: {term_raw} - Error: {term_error}")
            log_suspicious_activity(self.request, "invalid_search_term", f"Term: {term_raw}")
            # Usar termo vazio se inválido
            self.term = ""

        # Validação segura dos campos de busca
        campos_raw = self.request.GET.getlist("campos")
        self.campos = validate_search_fields(campos_raw)
        
        # Validação segura do nome do cliente
        cliente_raw = self.request.GET.get("cliente", "").strip()
        cliente_valid, self.cliente, cliente_error = validate_client_name(cliente_raw)
        
        if not cliente_valid:
            search_logger.warning(f"Invalid client name rejected: {cliente_raw} - Error: {cliente_error}")
            log_suspicious_activity(self.request, "invalid_client_name", f"Name: {cliente_raw}")
            self.cliente = ""
            
        if self.cliente:
            qs = qs.filter(cliente__first_name__icontains=self.cliente)

        # Aplicar filtro de termo de busca se válido
        if self.term:
            conditions = Q()
            if not self.campos or "titulo" in self.campos:
                conditions |= Q(titulo__icontains=self.term)
            if not self.campos or "descricao" in self.campos:
                conditions |= Q(descricao__icontains=self.term)
            if not self.campos or "categoria" in self.campos:
                conditions |= Q(categoria__nome__icontains=self.term)
            if not self.campos or "subcategoria" in self.campos:
                conditions |= Q(subcategoria__nome__icontains=self.term)
            qs = qs.filter(conditions)

        # Validação segura da localização
        local_raw = self.request.GET.get("local", "").strip()
        local_valid, self.local, local_error = validate_location(local_raw)
        
        if not local_valid:
            search_logger.warning(f"Invalid location rejected: {local_raw} - Error: {local_error}")
            log_suspicious_activity(self.request, "invalid_location", f"Location: {local_raw}")
            self.local = ""
            
        if self.local:
            qs = qs.filter(
                Q(cliente__cidade__icontains=self.local) |
                Q(cliente__bairro__icontains=self.local)
            )

        # Validação segura das coordenadas
        lat_raw = self.request.GET.get("lat")
        lon_raw = self.request.GET.get("lon")
        coords_valid, self.lat, self.lon, coords_error = validate_coordinates(lat_raw, lon_raw)
        
        if not coords_valid:
            search_logger.warning(f"Invalid coordinates rejected: lat={lat_raw}, lon={lon_raw} - Error: {coords_error}")
            log_suspicious_activity(self.request, "invalid_coordinates", f"lat={lat_raw}, lon={lon_raw}")
            self.lat = self.lon = None

        return qs.order_by("-data_criacao")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Usar valores validados e sanitizados
        ctx["term"] = getattr(self, 'term', '')
        ctx["state"] = getattr(self, 'state_sigla', 'TODOS')
        ctx["local"] = getattr(self, 'local', '')
        ctx["campos"] = getattr(self, 'campos', [])
        ctx["cliente"] = getattr(self, 'cliente', '')
        ctx["lat"] = getattr(self, 'lat', None) or ""
        ctx["lon"] = getattr(self, 'lon', None) or ""
        
        # Otimizar consulta de categorias - apenas campos necessários
        ctx["menu_categorias"] = Categoria.objects.only('id', 'nome', 'icone').all()
        ctx["opcoes_campos"] = ["titulo", "descricao", "categoria", "subcategoria"]
        
        # Contexto para filtro de status
        ctx["status_selecionados"] = getattr(self, 'status_selecionados', ['ativo'])
        ctx["opcoes_status"] = [
            {'value': choice[0], 'label': choice[1]} 
            for choice in Necessidade.status.field.choices
        ]
        
        return ctx


# Limpar cache de autocomplete quando houver atualizações relevantes
def clear_autocomplete_cache():
    """
    Função utilitária para limpar o cache de autocomplete.
    Deve ser chamada quando categorias ou necessidades são criadas/atualizadas.
    """
    # Limpar todos os caches que começam com 'autocomplete:'
    cache.delete_many(cache.get_many(['*']).keys())
    search_logger.info("Autocomplete cache cleared")


@require_http_methods(["GET"])
@rate_limit_decorator('autocomplete')
def autocomplete_search(request):
    """
    Endpoint AJAX para autocomplete inteligente com sugestões agrupadas por categoria.
    Implementa segurança contra XSS, rate limiting e cache para performance.
    """
    term_raw = request.GET.get('term', '').strip()
    
    # Validação de segurança do termo
    term_valid, term, term_error = validate_search_term(term_raw)
    
    if not term_valid:
        search_logger.warning(f"Invalid autocomplete term rejected: {term_raw} - Error: {term_error}")
        log_suspicious_activity(request, "invalid_autocomplete_term", f"Term: {term_raw}")
        return JsonResponse({
            'error': 'Termo de busca inválido',
            'results': []
        }, status=400)
    
    # Mínimo de 2 caracteres para busca
    if len(term) < 2:
        return JsonResponse({'results': []})
    
    # Verificar cache primeiro
    cache_key = f"autocomplete:{term.lower()}"  # termo já sanitizado
    cached_results = cache.get(cache_key)
    
    if cached_results:
        search_logger.info(f"Autocomplete cache hit for term: {term}")
        return JsonResponse(cached_results)
    
    # Log da busca para monitoramento
    search_logger.info(f"Autocomplete search for term: {term}")
    
    # Limitar resultados para performance
    max_results_per_type = 5
    results = []
    
    try:
        # Buscar em categorias - apenas campos necessários
        categorias = Categoria.objects.filter(
            nome__icontains=term
        ).only('id', 'nome', 'icone')[:max_results_per_type]
        
        for cat in categorias:
            results.append({
                'id': f"categoria_{cat.id}",
                'text': cat.nome,
                'type': 'categoria',
                'icon': cat.icone or 'fas fa-tags',
                'group': 'Categorias'
            })
        
        # Buscar em subcategorias - otimizada
        subcategorias = SubCategoria.objects.filter(
            nome__icontains=term
        ).select_related('categoria').only(
            'id', 'nome', 'categoria__nome', 'categoria__icone'
        )[:max_results_per_type]
        
        for subcat in subcategorias:
            results.append({
                'id': f"subcategoria_{subcat.id}",
                'text': f"{subcat.nome} ({subcat.categoria.nome})",
                'type': 'subcategoria',
                'icon': subcat.categoria.icone or 'fas fa-tag',
                'group': 'Subcategorias'
            })
        
        # Buscar títulos de necessidades populares - otimizada
        necessidades = Necessidade.objects.filter(
            titulo__icontains=term,
            status='ativo'
        ).only('titulo').distinct()[:max_results_per_type]
        
        for nec in necessidades:
            results.append({
                'id': f"titulo_{nec.titulo}",
                'text': nec.titulo,
                'type': 'titulo',
                'icon': 'fas fa-search',
                'group': 'Anúncios Similares'
            })
        
        # Agrupar resultados por tipo
        grouped_results = {}
        for result in results:
            group = result['group']
            if group not in grouped_results:
                grouped_results[group] = []
            grouped_results[group].append(result)
        
        response_data = {
            'results': grouped_results,
            'total': len(results)
        }
        
        # Cache por 5 minutos
        cache.set(cache_key, response_data, 300)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        search_logger.error(f"Error in autocomplete search: {str(e)}")
        log_suspicious_activity(request, "autocomplete_error", f"Error: {str(e)} | Term: {term}")
        
        return JsonResponse({
            'error': 'Erro interno no sistema de busca',
            'results': []
        }, status=500)