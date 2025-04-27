from django.views.generic import ListView
from django.db.models import Q, Prefetch
from ads.models import Necessidade, Categoria, AnuncioImagem

class NecessidadeSearchAllView(ListView):
    model = Necessidade
    template_name = "results.html"
    context_object_name = "anuncios"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            Necessidade.objects
            .filter(status="ativo")
            .select_related("categoria", "subcategoria", "cliente")
            .prefetch_related(
                Prefetch("imagens", queryset=AnuncioImagem.objects.order_by("id"))
            )
        )

        self.state_sigla = self.request.GET.get("state", "CE").upper()
        qs = qs.filter(cliente__estado=self.state_sigla)

        self.term = self.request.GET.get("q", "").strip()
        self.campos = self.request.GET.getlist("campos") or []
        
        self.cliente = self.request.GET.get("cliente", "").strip()
        if self.cliente:
            qs = qs.filter(cliente__first_name__icontains=self.cliente)

        

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

        self.local = self.request.GET.get("local", "").strip()
        if self.local:
            qs = qs.filter(
                Q(cliente__cidade__icontains=self.local) |
                Q(cliente__bairro__icontains=self.local)
            )

        return qs.order_by("-data_criacao")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["term"] = self.term
        ctx["state"] = self.state_sigla
        ctx["local"] = self.local
        ctx["campos"] = self.campos
        ctx["menu_categorias"] = Categoria.objects.all()
        ctx["opcoes_campos"] = ["titulo", "descricao", "categoria", "subcategoria"]
        ctx["cliente"] = self.cliente
        return ctx
