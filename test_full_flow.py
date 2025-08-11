#!/usr/bin/env python
"""
Script para testar todo o fluxo de negociação do sistema:
1. Criar 1 cliente e 1 fornecedor
2. Criar 1 anúncio/necessidade pelo cliente
3. Criar 1 orçamento pelo fornecedor
4. Cliente aceita o orçamento
5. Fornecedor confirma o orçamento
6. Cliente finaliza o anúncio
7. Ambos avaliam um ao outro

Este script usa o shell Django para simular todo o fluxo de negociação.
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()

from django.db import transaction
from users.models import User
from ads.models import Necessidade
from budgets.models import Orcamento, OrcamentoItem
from rankings.models import Avaliacao, AvaliacaoCriterio
from categories.models import Categoria, SubCategoria


def create_test_users():
    """Cria usuários de teste"""
    print("🔹 Criando usuários de teste...")
    
    # Cliente
    cliente = User.objects.create_user(
        email="cliente@test.com",
        password="teste123",
        first_name="João",
        last_name="Cliente",
        telefone="85999887766",
        is_client=True,
        is_supplier=False
    )
    print(f"✅ Cliente criado: {cliente.email} (ID: {cliente.id})")
    
    # Fornecedor
    fornecedor = User.objects.create_user(
        email="fornecedor@test.com",
        password="teste123",
        first_name="Maria",
        last_name="Fornecedora",
        telefone="85998776655",
        is_client=False,
        is_supplier=True
    )
    print(f"✅ Fornecedor criado: {fornecedor.email} (ID: {fornecedor.id})")
    
    return cliente, fornecedor


def create_test_necessidade(cliente):
    """Cria um anúncio/necessidade de teste"""
    print("🔹 Criando anúncio de teste...")
    
    # Buscar categoria existente ou criar uma
    categoria, _ = Categoria.objects.get_or_create(
        nome="Construção",
        defaults={"descricao": "Categoria de teste para construção"}
    )
    
    subcategoria, _ = SubCategoria.objects.get_or_create(
        nome="Material Elétrico",
        categoria=categoria,
        defaults={"descricao": "Subcategoria de teste para material elétrico"}
    )
    
    necessidade = Necessidade.objects.create(
        cliente=cliente,
        categoria=categoria,
        subcategoria=subcategoria,
        titulo="Compra de cabos elétricos",
        descricao="Necessito de cabos elétricos 2,5mm para instalação residencial",
        quantidade=100,
        unidade="m",
        marca="Qualquer",
        status="ativo"
    )
    
    print(f"✅ Anúncio criado: {necessidade.titulo} (ID: {necessidade.id})")
    return necessidade


def create_test_orcamento(fornecedor, necessidade):
    """Cria orçamento de teste"""
    print("🔹 Criando orçamento de teste...")
    
    # Criar orçamento
    orcamento = Orcamento.objects.create(
        fornecedor=fornecedor,
        anuncio=necessidade,
        prazo_validade=date.today() + timedelta(days=7),
        prazo_entrega=date.today() + timedelta(days=3),
        observacao="Orçamento de teste criado automaticamente",
        tipo_frete="fob",
        valor_frete=Decimal("50.00"),
        forma_pagamento="pix",
        condicao_pagamento="a_vista",
        tipo_venda="uso_consumo",
        status="pendente"
    )
    
    # Criar item do orçamento
    item = OrcamentoItem.objects.create(
        orcamento=orcamento,
        tipo="MAT",  # Material
        descricao="Cabo elétrico flexível 2,5mm",
        quantidade=Decimal("100.000"),
        unidade="m",
        valor_unitario=Decimal("5.50"),
        ncm="8544.42.00",
        icms_percentual=Decimal("18.00"),
        ipi_percentual=Decimal("5.00")
    )
    
    # Atualizar status do anúncio
    necessidade.status = "analisando_orcamentos"
    necessidade.save()
    
    print(f"✅ Orçamento criado: #{orcamento.id} (Valor total: R$ {orcamento.get_total_geral()})")
    print(f"   Item: {item.descricao} - {item.quantidade} {item.unidade} x R$ {item.valor_unitario}")
    return orcamento


def simulate_negotiation(cliente, fornecedor, orcamento):
    """Simula negociação: aceite pelo cliente e confirmação pelo fornecedor"""
    print("🔹 Simulando processo de negociação...")
    
    # 1. Cliente aceita o orçamento
    print("   📋 Cliente aceita o orçamento...")
    orcamento.status = "aceito_pelo_cliente"
    orcamento.save()
    
    orcamento.anuncio.status = "aguardando_confirmacao"
    orcamento.anuncio.save()
    print("   ✅ Orçamento aceito pelo cliente")
    
    # 2. Fornecedor confirma
    print("   📋 Fornecedor confirma o orçamento...")
    orcamento.status = "confirmado"
    orcamento.save()
    
    orcamento.anuncio.status = "em_atendimento"
    orcamento.anuncio.save()
    print("   ✅ Orçamento confirmado pelo fornecedor")
    
    # 3. Cliente finaliza (simula entrega/conclusão)
    print("   📋 Cliente finaliza o anúncio...")
    orcamento.anuncio.status = "finalizado"
    orcamento.anuncio.save()
    print("   ✅ Anúncio finalizado - pronto para avaliação")


def create_test_avaliacoes(cliente, fornecedor, necessidade):
    """Cria avaliações mútuas"""
    print("🔹 Criando avaliações mútuas...")
    
    # 1. Cliente avalia fornecedor
    print("   📋 Cliente avalia fornecedor...")
    avaliacao_fornecedor = Avaliacao.objects.create(
        usuario=cliente,
        avaliado=fornecedor,
        anuncio=necessidade,
        tipo_avaliacao="fornecedor"
    )
    
    # Critérios para avaliar fornecedor
    criterios_fornecedor = [
        ('qualidade_produto', 5),
        ('pontualidade_entrega', 4),
        ('atendimento', 5),
        ('precos_mercado', 4)
    ]
    
    for criterio, estrelas in criterios_fornecedor:
        AvaliacaoCriterio.objects.create(
            avaliacao=avaliacao_fornecedor,
            criterio=criterio,
            estrelas=estrelas
        )
    
    avaliacao_fornecedor.calcular_media()
    print(f"   ✅ Cliente avaliou fornecedor: {avaliacao_fornecedor.media_estrelas} estrelas")
    
    # 2. Fornecedor avalia cliente
    print("   📋 Fornecedor avalia cliente...")
    avaliacao_cliente = Avaliacao.objects.create(
        usuario=fornecedor,
        avaliado=cliente,
        anuncio=necessidade,
        tipo_avaliacao="cliente"
    )
    
    # Critérios para avaliar cliente
    criterios_cliente = [
        ('rapidez_respostas', 5),
        ('pagamento_acordado', 5),
        ('urbanidade_negociacao', 4)
    ]
    
    for criterio, estrelas in criterios_cliente:
        AvaliacaoCriterio.objects.create(
            avaliacao=avaliacao_cliente,
            criterio=criterio,
            estrelas=estrelas
        )
    
    avaliacao_cliente.calcular_media()
    print(f"   ✅ Fornecedor avaliou cliente: {avaliacao_cliente.media_estrelas} estrelas")
    
    return avaliacao_fornecedor, avaliacao_cliente


def display_results(cliente, fornecedor, necessidade, orcamento, avaliacoes):
    """Exibe resumo dos resultados"""
    print("\n" + "="*60)
    print("📊 RESUMO DO TESTE COMPLETO")
    print("="*60)
    
    print(f"\n�� USUÁRIOS CRIADOS:")
    print(f"   Cliente: {cliente.get_full_name()} ({cliente.email})")
    print(f"   Fornecedor: {fornecedor.get_full_name()} ({fornecedor.email})")
    
    print(f"\n📢 ANÚNCIO:")
    print(f"   Título: {necessidade.titulo}")
    print(f"   Status: {necessidade.get_status_display()}")
    print(f"   URL: http://localhost/necessidades/{necessidade.id}/")
    
    print(f"\n�� ORÇAMENTO:")
    print(f"   ID: #{orcamento.id}")
    print(f"   Status: {orcamento.get_status_display()}")
    print(f"   Valor total: R$ {orcamento.get_total_geral()}")
    print(f"   Itens: {orcamento.itens.count()}")
    
    print(f"\n⭐ AVALIAÇÕES:")
    print(f"   Cliente → Fornecedor: {avaliacoes[0].media_estrelas} estrelas")
    print(f"   Fornecedor → Cliente: {avaliacoes[1].media_estrelas} estrelas")
    
    print(f"\n🌐 ACESSOS PARA TESTE:")
    print(f"   Anúncio: http://localhost/necessidades/{necessidade.id}/")
    print(f"   Login Cliente: {cliente.email} / teste123")
    print(f"   Login Fornecedor: {fornecedor.email} / teste123")
    
    print("\n✅ FLUXO COMPLETO TESTADO COM SUCESSO!")
    print("="*60)


@transaction.atomic
def main():
    """Executa todo o fluxo de teste"""
    print("🚀 INICIANDO TESTE COMPLETO DO FLUXO DE NEGOCIAÇÃO")
    print("="*60)
    
    try:
        # Limpar dados de teste anteriores (opcional)
        print("🔹 Limpando dados de teste anteriores...")
        User.objects.filter(email__in=["cliente@test.com", "fornecedor@test.com"]).delete()
        print("   ✅ Dados limpos")
        
        # Executar fluxo completo
        cliente, fornecedor = create_test_users()
        necessidade = create_test_necessidade(cliente)
        orcamento = create_test_orcamento(fornecedor, necessidade)
        simulate_negotiation(cliente, fornecedor, orcamento)
        avaliacoes = create_test_avaliacoes(cliente, fornecedor, necessidade)
        
        # Exibir resultados
        display_results(cliente, fornecedor, necessidade, orcamento, avaliacoes)
        
    except Exception as e:
        print(f"❌ ERRO DURANTE EXECUÇÃO: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
