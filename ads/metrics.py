import calendar
import datetime
from django.utils import timezone
from django.db.models import Sum, Value, DecimalField, Count, F
from django.utils.timezone import now
from django.db.models.functions import Coalesce, TruncMonth
from collections import OrderedDict
from django.utils.formats import number_format
from ads.models import Necessidade
from budgets.models import Orcamento, OrcamentoItem
from users.models import User

def get_ads_metrics():
    total_ads = Necessidade.objects.count()
    active_ads = Necessidade.objects.filter(status='ativo').count()
    finished_ads = Necessidade.objects.filter(status='finalizado').count()
    total_budgets = Orcamento.objects.count()

    return dict(
        total_ads=total_ads,
        active_ads=active_ads,
        finished_ads=finished_ads,
        total_budgets=total_budgets
    )

def get_valores_metrics():
    # 1️⃣ Valor Total de Anúncios Finalizados: soma dos valores de orçamentos aceitos em anúncios finalizados
    # Calculando através dos itens dos orçamentos
    valor_total_transacoes_concluidas = OrcamentoItem.objects.filter(
        orcamento__status='confirmado',
        orcamento__anuncio__status='finalizado'
    ).aggregate(
        total=Coalesce(
            Sum(F('quantidade') * F('valor_unitario')), 
            Value(0, output_field=DecimalField())
        )
    )['total']

    # 2️⃣ Valor Total de Orçamentos Enviados: soma de todos os valores enviados, independente de aceitação
    valor_total_orcamentos_enviados = OrcamentoItem.objects.aggregate(
        total=Coalesce(
            Sum(F('quantidade') * F('valor_unitario')), 
            Value(0, output_field=DecimalField())
        )
    )['total']
    

    # 3️⃣ Valor Total de Transações em Andamento: orçamentos aceitos vinculados a anúncios NÃO finalizados
    valor_total_transacoes_andamento = OrcamentoItem.objects.filter(
        orcamento__status='confirmado',
        orcamento__anuncio__status__in=['em_atendimento']
    ).aggregate(
        total=Coalesce(
            Sum(F('quantidade') * F('valor_unitario')), 
            Value(0, output_field=DecimalField())
        )
    )['total']
   

    # 4️⃣ Taxa de Conversão de Anúncios (%): (anúncios finalizados ÷ total anúncios criados) * 100
    total_anuncios = Necessidade.objects.count() or 1  # evita divisão por zero
    total_anuncios_finalizados = Necessidade.objects.filter(status='finalizado').count()
    taxa_conversao = (total_anuncios_finalizados / total_anuncios) * 100

    # Retornando as métricas formatadas para exibição
    return dict(
        valor_total_transacoes_concluidas=number_format(valor_total_transacoes_concluidas, decimal_pos=2, force_grouping=True),
        valor_total_orcamentos_enviados=number_format(valor_total_orcamentos_enviados, decimal_pos=2, force_grouping=True),
        valor_total_transacoes_andamento=number_format(valor_total_transacoes_andamento, decimal_pos=2, force_grouping=True),
        taxa_conversao=number_format(taxa_conversao, decimal_pos=2),
    )

def get_valores_por_mes():
     # 1️⃣ Definir os últimos 12 meses
    hoje = now().date()
    meses = []
    for i in range(11, -1, -1):  # de 11 até 0
        mes_ref = hoje - datetime.timedelta(days=i * 30)  # simplificação aproximada
        primeiro_dia = mes_ref.replace(day=1)
        meses.append(primeiro_dia)

    # 2️⃣ Consultar o banco - usando OrcamentoItem ao invés de campo valor direto
    qs = OrcamentoItem.objects.filter(
        orcamento__status='confirmado',
        orcamento__anuncio__status='finalizado'
    ).annotate(
        mes=TruncMonth('orcamento__data_criacao')
    ).values('mes').annotate(
        total=Sum(F('quantidade') * F('valor_unitario'))
    )

    # 3️⃣ Criar dicionário com meses e valores encontrados
    dados_db = {registro['mes'].date(): float(registro['total']) for registro in qs if registro['total']}

    # 4️⃣ Garantir todos os meses (preencher zero onde faltar)
    labels = []
    valores = []
    for mes in meses:
        mes_nome = f"{calendar.month_abbr[mes.month]}/{mes.year}"
        labels.append(mes_nome)
        valores.append(dados_db.get(mes, 0))

    return {
        'labels': labels,
        'valores': valores,
    }

def get_quantidade_anuncios_finalizados_por_categoria():
    # Consulta agrupando categoria
    qs = Necessidade.objects.filter(
        status='finalizado'
    ).values('categoria__nome').annotate(
        total=Count('id')
    ).order_by('-total')[:10]

    # Cria as listas de labels e valores
    labels = []
    valores = []
    for item in qs:
        labels.append(item['categoria__nome'])
        valores.append(item['total'])

    return {
        'labels': labels,
        'valores': valores,
    }

def get_quantidade_usuarios_por_tipo():
    # Usuários que são só clientes
    so_clientes = User.objects.filter(is_client=True, is_supplier=False).count()
    # Usuários que são só fornecedores
    so_fornecedores = User.objects.filter(is_client=False, is_supplier=True).count()
    # Usuários que são ambos
    ambos = User.objects.filter(is_client=True, is_supplier=True).count()
    # Usuários que não são nem clientes nem fornecedores
    nenhum = User.objects.filter(is_client=False, is_supplier=False).count()
    # Total geral
    total = so_clientes + so_fornecedores + ambos + nenhum

    return {
        'labels': ['Só Clientes', 'Só Fornecedores', 'Clientes e Fornecedores', 'Nenhum dos dois'],
        'valores': [so_clientes, so_fornecedores, ambos, nenhum],
        'total': total
    }

def get_anuncios_criados_vs_finalizados():
    today = timezone.now().date()
    meses_labels = []
    criados = []
    finalizados = []

    for i in range(11, -1, -1):  # últimos 12 meses (12 → 0)
        primeiro_dia = (today.replace(day=1) - timezone.timedelta(days=30*i)).replace(day=1)
        mes = primeiro_dia.month
        ano = primeiro_dia.year
        label = f"{calendar.month_abbr[mes]}/{ano}"
        meses_labels.append(label)

        count_criados = Necessidade.objects.filter(
            data_criacao__year=ano,
            data_criacao__month=mes
        ).count()

        count_finalizados = Necessidade.objects.filter(
            data_criacao__year=ano,
            data_criacao__month=mes,
            status='finalizado'
        ).count()

        criados.append(count_criados)
        finalizados.append(count_finalizados)

    return {
        'labels': meses_labels,
        'criados': criados,
        'finalizados': finalizados
    }
