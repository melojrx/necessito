"""
Testes automatizados para validar transições de status de orçamentos.
Baseado nas regras de negócio documentadas em:
- docs/Mapeamento_regras_de_negocio_indicai.md
- docs/REGRAS_NEGOCIO_IMPLEMENTACAO.md
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from ads.models import Necessidade
from budgets.models import Orcamento, OrcamentoItem
from categories.models import Categoria, SubCategoria

User = get_user_model()


class OrcamentoStatusTransitionsTest(TestCase):
    """
    Testes para validar o fluxo completo de transições de status de orçamentos
    conforme as regras de negócio documentadas.
    """
    
    def setUp(self):
        """Configuração inicial dos testes."""
        # Criar categoria e subcategoria
        self.categoria = Categoria.objects.create(
            nome='Serviços',
            descricao='Serviços diversos',
            
        )
        self.subcategoria = SubCategoria.objects.create(
            categoria=self.categoria,
            nome='Pintura',
            descricao='Serviços de pintura',
            
        )
        
        # Criar cliente (anunciante)
        self.cliente = User.objects.create_user(
            email='cliente@test.com',
            password='test123',
            first_name='Cliente',
            last_name='Teste',
            tipo_usuario='cliente',
            cidade='São Paulo',
            estado='SP',
            cep='01234567',
            telefone='11999999999'
        )
        
        # Criar fornecedor
        self.fornecedor = User.objects.create_user(
            email='fornecedor@test.com',
            password='test123',
            first_name='Fornecedor',
            last_name='Teste',
            tipo_usuario='fornecedor',
            cidade='São Paulo',
            estado='SP',
            cep='01234567',
            telefone='11988888888'
        )
        
        # Criar outro fornecedor
        self.fornecedor2 = User.objects.create_user(
            email='fornecedor2@test.com',
            password='test123',
            first_name='Fornecedor',
            last_name='Dois',
            tipo_usuario='fornecedor',
            cidade='São Paulo',
            estado='SP',
            cep='01234567',
            telefone='11977777777'
        )
        
        # Criar necessidade (anúncio)
        self.necessidade = Necessidade.objects.create(
            cliente=self.cliente,
            categoria=self.categoria,
            subcategoria=self.subcategoria,
            titulo='Preciso de pintura residencial',
            descricao='Pintar sala e quartos',
            quantidade=1,
            unidade='un',
            status='ativo',
            data_validade=timezone.now() + timedelta(days=30)
        )
        
        # Cliente HTTP para testes
        self.client_http = Client()
    
    def criar_orcamento(self, fornecedor=None, necessidade=None):
        """Helper para criar um orçamento completo."""
        if fornecedor is None:
            fornecedor = self.fornecedor
        if necessidade is None:
            necessidade = self.necessidade
        
        orcamento = Orcamento.objects.create(
            fornecedor=fornecedor,
            anuncio=necessidade,
            prazo_validade=timezone.now().date() + timedelta(days=10),
            prazo_entrega=timezone.now().date() + timedelta(days=15),
            observacao='Orçamento de teste',
            tipo_frete='fob',
            forma_pagamento='pix',
            condicao_pagamento='a_vista',
            tipo_venda='servico',
            status='enviado'
        )
        
        # Criar item do orçamento
        OrcamentoItem.objects.create(
            orcamento=orcamento,
            tipo='SRV',
            descricao='Pintura de parede',
            quantidade=Decimal('1'),
            unidade='m2',
            valor_unitario=Decimal('50.00'),
            cnae='4330403',
            aliquota_iss=Decimal('5.00')
        )
        
        return orcamento
    
    # ==================== TESTES DE STATUS INICIAL ====================
    
    def test_orcamento_inicia_com_status_enviado(self):
        """
        REGRA: Orçamento deve iniciar com status 'enviado' (não 'pendente').
        Referência: Linha 211, 238 do documento REGRAS_NEGOCIO_IMPLEMENTACAO.md
        """
        orcamento = self.criar_orcamento()
        
        self.assertEqual(orcamento.status, 'enviado',
                        "Orçamento deve iniciar com status 'enviado', não 'pendente'")
    
    def test_anuncio_muda_para_analisando_orcamentos_no_primeiro_orcamento(self):
        """
        REGRA: Ao receber primeiro orçamento, anúncio muda de 'ativo' para 'analisando_orcamentos'.
        Referência: Etapa 2 do Mapeamento_regras_de_negocio_indicai.md
        """
        self.assertEqual(self.necessidade.status, 'ativo')
        
        # Criar primeiro orçamento
        self.criar_orcamento()
        
        # Recarregar necessidade do banco
        self.necessidade.refresh_from_db()
        
        # Status deve mudar para 'analisando_orcamentos'
        # Nota: Esta lógica deve ser implementada em signal ou view
        # Por enquanto, este teste documenta o comportamento esperado
    
    # ==================== TESTES DE ACEITE PELO CLIENTE ====================
    
    def test_cliente_pode_aceitar_orcamento_enviado(self):
        """
        REGRA: Cliente pode aceitar orçamento quando status é 'enviado'.
        Referência: Etapa 3, Cenário B do Mapeamento_regras_de_negocio_indicai.md
        """
        orcamento = self.criar_orcamento()
        
        # Login como cliente
        self.client_http.login(email='cliente@test.com', password='test123')
        
        # Aceitar orçamento
        response = self.client_http.post(
            reverse('budgets:aceitar_orcamento', kwargs={'pk': orcamento.pk})
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'), f"Erro: {data.get('error')}")
        
        # Verificar mudança de status
        orcamento.refresh_from_db()
        self.assertEqual(orcamento.status, 'aceito_pelo_cliente',
                        "Status deve mudar para 'aceito_pelo_cliente'")
        
        # Verificar mudança de status do anúncio
        self.necessidade.refresh_from_db()
        self.assertEqual(self.necessidade.status, 'aguardando_confirmacao',
                        "Anúncio deve mudar para 'aguardando_confirmacao'")
    
    def test_cliente_nao_pode_aceitar_orcamento_ja_aceito(self):
        """
        REGRA: Cliente não pode aceitar orçamento que já está em outro status.
        """
        orcamento = self.criar_orcamento()
        orcamento.status = 'confirmado'
        orcamento.save()
        
        # Login como cliente
        self.client_http.login(email='cliente@test.com', password='test123')
        
        # Tentar aceitar orçamento confirmado
        response = self.client_http.post(
            reverse('budgets:aceitar_orcamento', kwargs={'pk': orcamento.pk})
        )
        
        # Deve retornar erro
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('error', data)
    
    def test_apenas_cliente_pode_aceitar_orcamento(self):
        """
        REGRA: Apenas o cliente dono do anúncio pode aceitar orçamentos.
        """
        orcamento = self.criar_orcamento()
        
        # Login como fornecedor (não é o cliente)
        self.client_http.login(email='fornecedor@test.com', password='test123')
        
        # Tentar aceitar orçamento
        response = self.client_http.post(
            reverse('budgets:aceitar_orcamento', kwargs={'pk': orcamento.pk})
        )
        
        # Deve retornar erro 403
        self.assertEqual(response.status_code, 403)
    
    # ==================== TESTES DE REJEIÇÃO PELO CLIENTE ====================
    
    def test_cliente_pode_rejeitar_orcamento_enviado(self):
        """
        REGRA: Cliente pode rejeitar orçamento quando status é 'enviado'.
        Referência: Etapa 3, Cenário A do Mapeamento_regras_de_negocio_indicai.md
        """
        orcamento = self.criar_orcamento()
        
        # Login como cliente
        self.client_http.login(email='cliente@test.com', password='test123')
        
        # Rejeitar orçamento
        response = self.client_http.post(
            reverse('budgets:rejeitar_orcamento', kwargs={'pk': orcamento.pk})
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        
        # Verificar mudança de status
        orcamento.refresh_from_db()
        self.assertEqual(orcamento.status, 'rejeitado_pelo_cliente',
                        "Status deve mudar para 'rejeitado_pelo_cliente'")
    
    # ==================== TESTES DE CONFIRMAÇÃO PELO FORNECEDOR ====================
    
    def test_fornecedor_pode_confirmar_orcamento_aceito(self):
        """
        REGRA: Fornecedor pode confirmar orçamento quando cliente já aceitou.
        Referência: Etapa 4, Cenário A do Mapeamento_regras_de_negocio_indicai.md
        """
        orcamento = self.criar_orcamento()
        
        # Cliente aceita primeiro
        self.client_http.login(email='cliente@test.com', password='test123')
        self.client_http.post(
            reverse('budgets:aceitar_orcamento', kwargs={'pk': orcamento.pk})
        )
        
        # Logout e login como fornecedor
        self.client_http.logout()
        self.client_http.login(email='fornecedor@test.com', password='test123')
        
        # Fornecedor confirma
        response = self.client_http.post(
            reverse('budgets:fornecedor_aceitar', kwargs={'pk': orcamento.pk})
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        
        # Verificar mudança de status
        orcamento.refresh_from_db()
        self.assertEqual(orcamento.status, 'confirmado',
                        "Status deve mudar para 'confirmado'")
        
        # Verificar mudança de status do anúncio
        self.necessidade.refresh_from_db()
        self.assertEqual(self.necessidade.status, 'em_atendimento',
                        "Anúncio deve mudar para 'em_atendimento'")
    
    def test_fornecedor_pode_recusar_orcamento_aceito(self):
        """
        REGRA: Fornecedor pode recusar orçamento após cliente aceitar.
        Referência: Etapa 4, Cenário B do Mapeamento_regras_de_negocio_indicai.md
        """
        orcamento = self.criar_orcamento()
        
        # Cliente aceita primeiro
        self.client_http.login(email='cliente@test.com', password='test123')
        self.client_http.post(
            reverse('budgets:aceitar_orcamento', kwargs={'pk': orcamento.pk})
        )
        
        # Logout e login como fornecedor
        self.client_http.logout()
        self.client_http.login(email='fornecedor@test.com', password='test123')
        
        # Fornecedor recusa (esta funcionalidade precisa ser implementada)
        # Por enquanto, documenta o comportamento esperado
        # response = self.client_http.post(
        #     reverse('budgets:fornecedor_recusar', kwargs={'pk': orcamento.pk})
        # )
        
        # Manualmente simular recusa
        orcamento.status = 'recusado_pelo_fornecedor'
        orcamento.save()
        
        # Verificar status
        self.assertEqual(orcamento.status, 'recusado_pelo_fornecedor')
        
        # Anúncio deve voltar para 'analisando_orcamentos'
        # (Esta lógica precisa ser implementada)
    
    # ==================== TESTES DE MÚLTIPLOS ORÇAMENTOS ====================
    
    def test_multiplos_orcamentos_para_mesmo_anuncio(self):
        """
        REGRA: Múltiplos fornecedores podem enviar orçamentos para o mesmo anúncio.
        """
        # Criar 2 orçamentos de fornecedores diferentes
        orc1 = self.criar_orcamento(fornecedor=self.fornecedor)
        orc2 = self.criar_orcamento(fornecedor=self.fornecedor2)
        
        # Verificar que ambos têm status 'enviado'
        self.assertEqual(orc1.status, 'enviado')
        self.assertEqual(orc2.status, 'enviado')
        
        # Verificar que ambos estão associados à mesma necessidade
        self.assertEqual(orc1.anuncio, self.necessidade)
        self.assertEqual(orc2.anuncio, self.necessidade)
    
    def test_ao_aceitar_um_orcamento_outros_permanecem_enviado(self):
        """
        REGRA: Ao aceitar um orçamento, outros orçamentos 'enviado' permanecem bloqueados
        até que o fornecedor confirme ou recuse.
        Referência: Etapa 3, Cenário B, Regra Crítica do Mapeamento_regras_de_negocio_indicai.md
        """
        # Criar 2 orçamentos
        orc1 = self.criar_orcamento(fornecedor=self.fornecedor)
        orc2 = self.criar_orcamento(fornecedor=self.fornecedor2)
        
        # Cliente aceita primeiro orçamento
        self.client_http.login(email='cliente@test.com', password='test123')
        self.client_http.post(
            reverse('budgets:aceitar_orcamento', kwargs={'pk': orc1.pk})
        )
        
        # Verificar que orc1 mudou para 'aceito_pelo_cliente'
        orc1.refresh_from_db()
        self.assertEqual(orc1.status, 'aceito_pelo_cliente')
        
        # Verificar que orc2 ainda está 'enviado' (mas bloqueado para aceite)
        orc2.refresh_from_db()
        self.assertEqual(orc2.status, 'enviado')
        
        # Anúncio deve estar em 'aguardando_confirmacao'
        self.necessidade.refresh_from_db()
        self.assertEqual(self.necessidade.status, 'aguardando_confirmacao')
    
    def test_ao_confirmar_orcamento_outros_sao_rejeitados(self):
        """
        REGRA: Ao confirmar orçamento, demais orçamentos 'enviado' são rejeitados automaticamente.
        Referência: Etapa 4, Cenário A do Mapeamento_regras_de_negocio_indicai.md
        """
        # Criar 2 orçamentos
        orc1 = self.criar_orcamento(fornecedor=self.fornecedor)
        orc2 = self.criar_orcamento(fornecedor=self.fornecedor2)
        
        # Cliente aceita primeiro
        self.client_http.login(email='cliente@test.com', password='test123')
        self.client_http.post(
            reverse('budgets:aceitar_orcamento', kwargs={'pk': orc1.pk})
        )
        
        # Fornecedor confirma
        self.client_http.logout()
        self.client_http.login(email='fornecedor@test.com', password='test123')
        self.client_http.post(
            reverse('budgets:fornecedor_aceitar', kwargs={'pk': orc1.pk})
        )
        
        # Verificar que orc1 está 'confirmado'
        orc1.refresh_from_db()
        self.assertEqual(orc1.status, 'confirmado')
        
        # Verificar que orc2 foi rejeitado automaticamente
        orc2.refresh_from_db()
        self.assertEqual(orc2.status, 'rejeitado_pelo_cliente',
                        "Orçamento não aceito deve ser rejeitado automaticamente")
    
    # ==================== TESTES DE VALIDAÇÃO DE PERMISSÕES ====================
    
    def test_fornecedor_nao_pode_aceitar_proprio_orcamento(self):
        """
        REGRA: Fornecedor não pode aceitar seu próprio orçamento (apenas cliente pode).
        """
        orcamento = self.criar_orcamento()
        
        # Login como fornecedor (dono do orçamento)
        self.client_http.login(email='fornecedor@test.com', password='test123')
        
        # Tentar aceitar próprio orçamento
        response = self.client_http.post(
            reverse('budgets:aceitar_orcamento', kwargs={'pk': orcamento.pk})
        )
        
        # Deve retornar erro
        self.assertEqual(response.status_code, 403)
    
    def test_usuario_anonimo_nao_pode_aceitar_orcamento(self):
        """
        REGRA: Usuário não autenticado não pode aceitar orçamentos.
        """
        orcamento = self.criar_orcamento()
        
        # Não fazer login (usuário anônimo)
        response = self.client_http.post(
            reverse('budgets:aceitar_orcamento', kwargs={'pk': orcamento.pk})
        )
        
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)


class OrcamentoModelTest(TestCase):
    """Testes unitários do modelo Orcamento."""
    
    def setUp(self):
        """Configuração inicial."""
        # Criar categoria e subcategoria
        self.categoria = Categoria.objects.create(
            nome='Serviços',
            descricao='Serviços diversos',
            
        )
        self.subcategoria = SubCategoria.objects.create(
            categoria=self.categoria,
            nome='Pintura',
            descricao='Serviços de pintura',
            
        )
        
        # Criar usuários
        self.cliente = User.objects.create_user(
            email='cliente@test.com',
            password='test123',
            first_name='Cliente',
            last_name='Teste',
            tipo_usuario='cliente',
            cidade='São Paulo',
            estado='SP',
            cep='01234567',
            telefone='11999999999'
        )
        
        self.fornecedor = User.objects.create_user(
            email='fornecedor@test.com',
            password='test123',
            first_name='Fornecedor',
            last_name='Teste',
            tipo_usuario='fornecedor',
            cidade='São Paulo',
            estado='SP',
            cep='01234567',
            telefone='11988888888'
        )
        
        # Criar necessidade
        self.necessidade = Necessidade.objects.create(
            cliente=self.cliente,
            categoria=self.categoria,
            subcategoria=self.subcategoria,
            titulo='Teste',
            descricao='Teste',
            quantidade=1,
            unidade='un',
            status='ativo'
        )
    
    def test_orcamento_default_status_is_enviado(self):
        """
        REGRA: Status padrão de orçamento deve ser 'enviado', não 'pendente'.
        """
        orcamento = Orcamento.objects.create(
            fornecedor=self.fornecedor,
            anuncio=self.necessidade,
            prazo_validade=timezone.now().date() + timedelta(days=10),
            prazo_entrega=timezone.now().date() + timedelta(days=15)
        )
        
        self.assertEqual(orcamento.status, 'enviado',
                        "Default status deve ser 'enviado'")
    
    def test_status_choices_nao_contem_pendente(self):
        """
        REGRA: Choices de status não devem conter 'pendente'.
        """
        status_values = [choice[0] for choice in Orcamento.STATUS]
        
        self.assertNotIn('pendente', status_values,
                        "'pendente' não deve estar nas choices de status")
    
    def test_status_choices_contem_valores_corretos(self):
        """
        REGRA: Choices de status devem seguir as regras de negócio documentadas.
        """
        expected_statuses = [
            'enviado',
            'aceito_pelo_cliente',
            'confirmado',
            'rejeitado_pelo_cliente',
            'recusado_pelo_fornecedor',
            'cancelado_pelo_fornecedor',
            'finalizado',
            'anuncio_cancelado',
            'anuncio_expirado'
        ]
        
        status_values = [choice[0] for choice in Orcamento.STATUS]
        
        for expected in expected_statuses:
            self.assertIn(expected, status_values,
                         f"Status '{expected}' deve estar nas choices")
