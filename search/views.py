from django.views.generic import ListView
from django.contrib import messages
from django.db.models import Q, Prefetch
from ads.models import Necessidade, Categoria, AnuncioImagem
import math

class NecessidadeSearchAllView(ListView):
    model = Necessidade
    template_name = "results.html"
    context_object_name = "anuncios"
    paginate_by = 20

    def get_queryset(self):
        # Iniciar com todos os anúncios sem filtro fixo de status
        qs = (
            Necessidade.objects
            .select_related("categoria", "subcategoria", "cliente")
            .prefetch_related(
                Prefetch("imagens", queryset=AnuncioImagem.objects.order_by("id"))
            )
        )

        # Filtro de status - agora com valor padrão "ativo" se não for especificado
        self.status = self.request.GET.get("status", "ativo").strip()
        if self.status:
            qs = qs.filter(status=self.status)

        # Filtro de estado
        self.state_sigla = self.request.GET.get("state", "todos").upper()
        if self.state_sigla != "TODOS":
            qs = qs.filter(cliente__estado=self.state_sigla)

        # Filtro por cliente
        self.cliente = self.request.GET.get("cliente", "").strip()
        if self.cliente:
            qs = qs.filter(cliente__first_name__icontains=self.cliente)

        # Filtro por termo de busca
        self.term = self.request.GET.get("q", "").strip()
        self.campos = self.request.GET.getlist("campos") or []
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

        # Filtro por localidade
        self.local = self.request.GET.get("local", "").strip()
        if self.local:
            qs = qs.filter(
                Q(cliente__cidade__icontains=self.local) |
                Q(cliente__bairro__icontains=self.local)
            )

        # Filtro por geolocalização
        lat = self.request.GET.get("lat")
        lon = self.request.GET.get("lon")
        raio_km = self.request.GET.get("raio", "0")

        # Exibe alerta se raio > 0 mas sem localização
        if raio_km and float(raio_km) > 0 and (not lat or not lon):
            messages.warning(self.request, "Para aplicar o filtro de raio, é necessário ativar sua localização.")

        if lat and lon and raio_km:
            try:
                lat = float(lat)
                lon = float(lon)
                raio_km = float(raio_km)

                if raio_km > 0:
                    def haversine(lat1, lon1, lat2, lon2):
                        R = 6371
                        dlat = math.radians(lat2 - lat1)
                        dlon = math.radians(lon2 - lon1)
                        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
                        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                        return R * c

                    resultado_ids = []
                    for anuncio in qs:
                        cliente = anuncio.cliente
                        if cliente.lat and cliente.lon:
                            distancia = haversine(lat, lon, cliente.lat, cliente.lon)
                            if distancia <= raio_km:
                                resultado_ids.append(anuncio.id)

                    qs = qs.filter(id__in=resultado_ids) if resultado_ids else Necessidade.objects.none()

            except (ValueError, TypeError):
                pass

        return qs.order_by("-data_criacao")

    def get_context_data(self, **kwargs):
        from search.models import State
        
        ctx = super().get_context_data(**kwargs)
        ctx["term"] = self.term
        ctx["state"] = self.state_sigla
        ctx["local"] = self.local
        ctx["campos"] = self.campos
        ctx["cliente"] = self.cliente
        ctx["lat"] = self.request.GET.get("lat", "")
        ctx["lon"] = self.request.GET.get("lon", "")
        ctx["raio"] = self.request.GET.get("raio", "0")
        ctx["menu_categorias"] = Categoria.objects.all()
        ctx["opcoes_campos"] = ["titulo", "descricao", "categoria", "subcategoria"]
        ctx["status"] = self.status
        
        # Adicionar nome amigável do estado
        if self.state_sigla and self.state_sigla != "TODOS":
            try:
                state_obj = State.objects.get(abbreviation=self.state_sigla)
                ctx["state_display"] = f"{state_obj.name} ({self.state_sigla})"
            except State.DoesNotExist:
                ctx["state_display"] = self.state_sigla
        else:
            ctx["state_display"] = "Todos os estados"

        return ctx