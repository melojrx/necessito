from django.core.management.base import BaseCommand
from categories.models import Categoria

class Command(BaseCommand):
    help = "Preenche automaticamente os ícones das categorias com base em nomes conhecidos"

    icones_por_categoria = {
        "Acabamentos de Fachadas": "fas fa-brush",
        "Acessibilidade": "fas fa-wheelchair",
        "Aquecimento e Ventilação": "fas fa-fan",
        "Cidades Inteligentes": "fas fa-city",
        "Climatização e Ventilação": "fas fa-temperature-high",
        "Construção Modular": "fas fa-cubes",
        "Construção de Edificações Comerciais": "fas fa-building",
        "Construção de Escolas": "fas fa-school",
        "Construção de Infraestrutura": "fas fa-road",
        "Construção de Residências": "fas fa-house-chimney",
        "Consultoria Ambiental": "fas fa-leaf",
        "Consultoria e Projetos": "fas fa-lightbulb",
        "Demolição e Desmontagem": "fas fa-hammer",
        "Edificações Industriais": "fas fa-industry",
        "Edificações de Saúde": "fas fa-hospital",
        "Equipamentos de Construção": "fas fa-truck-monster",
        "Estrutura e Fundações": "fas fa-layer-group",
        "Fundação e Subsolo": "fas fa-mountain",
        "Gestão de Infraestrutura": "fas fa-network-wired",
        "Gestão de Obras": "fas fa-clipboard-check",
        "Gestão de Projetos": "fas fa-diagram-project",
        "Gestão de Resíduos de Construção": "fas fa-dumpster",
        "Imóveis Comerciais": "fas fa-building-circle-check",
        "Infraestrutura de Transportes": "fas fa-truck",
        "Instalações Elétricas": "fas fa-bolt",
        "Instalações Hidrossanitárias": "fas fa-shower",
        "Logística e Transporte": "fas fa-boxes-packing",
        "Manutenção de Infraestruturas": "fas fa-tools",
        "Manutenção e Reforma": "fas fa-screwdriver-wrench",
        "Materiais de Construção": "fas fa-bricks",
        "Materiais para Acabamento": "fas fa-paint-roller",
        "Paisagismo Vertical": "fas fa-tree",
        "Paisagismo e Áreas Externas": "fas fa-seedling",
        "Planejamento de Obras": "fas fa-calendar-check",
        "Produtos Sustentáveis": "fas fa-recycle",
        "Projetos Urbanos": "fas fa-draw-polygon",
        "Proteção Contra Incêndios": "fas fa-fire-extinguisher",
        "Reabilitação de Estruturas": "fas fa-hard-hat",
        "Revestimentos": "fas fa-fill-drip",
        "Segurança no Trabalho": "fas fa-user-shield",
        "Sistemas de Controle e Automação": "fas fa-microchip",
        "Sistemas de Energia Solar": "fas fa-solar-panel",
        "Sistemas de Energias Renováveis": "fas fa-wind",
        "Sistemas de Impermeabilização": "fas fa-water",
        "Sistemas de Reutilização": "fas fa-recycle",
        "Tecnologia e Inovação": "fas fa-robot",
        "Tecnologias de Isolamento": "fas fa-temperature-low",
        "Telecomunicações e Redes": "fas fa-signal",
        "Vidraria e Esquadrias": "fas fa-window-maximize",
        "Áreas de Lazer e Entretenimento": "fas fa-person-swimming",
    }

    def handle(self, *args, **kwargs):
        atualizados = 0
        for nome, icone in self.icones_por_categoria.items():
            try:
                categoria = Categoria.objects.get(nome=nome)
                categoria.icone = icone
                categoria.save()
                atualizados += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Categoria '{nome}' atualizada com ícone: {icone}"))
            except Categoria.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"✗ Categoria '{nome}' não encontrada"))

        self.stdout.write(self.style.SUCCESS(f"\n✔ {atualizados} categorias atualizadas com sucesso."))
