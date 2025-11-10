"""
Testes simples para validar status de orçamentos.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from budgets.models import Orcamento


class OrcamentoStatusTest(TestCase):
    """Testes simples de status de orçamento."""
    
    def test_status_default_is_enviado(self):
        """
        REGRA CRÍTICA: Status padrão deve ser 'enviado', não 'pendente'.
        Referência: budgets/models.py linha 74, default='enviado'
        """
        # Status definido no modelo
        field = Orcamento._meta.get_field('status')
        self.assertEqual(field.default, 'enviado',
                        "Default status DEVE ser 'enviado', não 'pendente'")
    
    def test_status_choices_nao_contem_pendente(self):
        """
        REGRA: Choices de status NÃO devem conter 'pendente'.
        Referência: Migration 0012_update_orcamento_status_choices.py
        """
        status_values = [choice[0] for choice in Orcamento.STATUS]
        
        self.assertNotIn('pendente', status_values,
                        "'pendente' NÃO deve estar nas choices de status")
        
        print("\n✅ Status disponíveis:")
        for status, display in Orcamento.STATUS:
            print(f"   - {status}: {display}")
    
    def test_status_choices_contem_enviado(self):
        """
        REGRA: Choices DEVEM conter 'enviado'.
        """
        status_values = [choice[0] for choice in Orcamento.STATUS]
        
        self.assertIn('enviado', status_values,
                     "'enviado' DEVE estar nas choices de status")
    
    def test_status_choices_seguem_regras_negocio(self):
        """
        REGRA: Choices devem seguir as regras de negócio documentadas.
        Referência: docs/Mapeamento_regras_de_negocio_indicai.md
        """
        expected_statuses = [
            'enviado',                      # Fornecedor enviou proposta
            'aceito_pelo_cliente',          # Cliente selecionou orçamento
            'confirmado',                   # Orçamento vencedor (fornecedor confirmou)
            'rejeitado_pelo_cliente',       # Cliente não aceitou
            'recusado_pelo_fornecedor',     # Fornecedor não pôde confirmar
            'cancelado_pelo_fornecedor',    # Fornecedor retirou antes do aceite
            'finalizado',                   # Serviço concluído
            'anuncio_cancelado',           # Anúncio foi cancelado
            'anuncio_expirado'             # Anúncio expirou
        ]
        
        status_values = [choice[0] for choice in Orcamento.STATUS]
        
        for expected in expected_statuses:
            self.assertIn(expected, status_values,
                         f"Status '{expected}' DEVE estar nas choices")
        
        print("\n✅ Todos os status obrigatórios estão presentes")
    
    def test_status_display_names(self):
        """
        TESTE: Verificar nomes de exibição dos status.
        """
        status_dict = dict(Orcamento.STATUS)
        
        self.assertEqual(status_dict['enviado'], 'Enviado')
        self.assertEqual(status_dict['aceito_pelo_cliente'], 'Aceito pelo cliente')
        self.assertEqual(status_dict['confirmado'], 'Confirmado')
        self.assertEqual(status_dict['rejeitado_pelo_cliente'], 'Rejeitado pelo cliente')
        
        print("\n✅ Nomes de exibição corretos")
