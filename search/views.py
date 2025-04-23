# search/views.py
from django.views.generic import ListView
from django.db.models import Q, Prefetch
from ads.models import Necessidade, Categoria, AnuncioImagem

class NecessidadeSearchAllView(ListView):
    """
    Busca global: termo + estado (obrigatório) e exibe resultados
    mais novos primeiro.
    - Termo pode aparecer no título, descrição, categoria ou sub-categoria.
    - Estado vem do dropdown (?state=CE).  Default = CE.
    """
    model = Necessidade
    template_name = "results.html"
    context_object_name = "anuncios"
    paginate_by = 20                       

    # ---------- filtros ----------
    def get_queryset(self):
        qs = (
            Necessidade.objects
            .filter(status="ativo")        # só anúncios ativos
            .select_related("categoria", "subcategoria", "cliente")
            .prefetch_related(
                Prefetch("imagens",
                         queryset=AnuncioImagem.objects.order_by("id"))
            )
        )

        # estado (sigla do usuário que publicou o anúncio)
        self.state_sigla = self.request.GET.get("state", "CE").upper()
        qs = qs.filter(cliente__estado=self.state_sigla)

        # termo livre
        self.term = self.request.GET.get("q", "").strip()
        if self.term:
            qs = qs.filter(
                Q(titulo__icontains=self.term) |
                Q(descricao__icontains=self.term) |
                Q(categoria__nome__icontains=self.term) |
                Q(subcategoria__nome__icontains=self.term)
            )

        return qs.order_by("-data_criacao")     # mais novo → mais antigo

    # ---------- extras para o template ----------
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["term"]       = self.term
        ctx["state"]      = self.state_sigla
        ctx["categorias"] = Categoria.objects.all()   # menu lateral
        return ctx
