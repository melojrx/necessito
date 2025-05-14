from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from users.models import User
from categories.models import Categoria, SubCategoria
from ads.models import Necessidade
from budgets.models import Orcamento
from rankings.models import Avaliacao


class APITestCase(APITestCase):
    """
    Testes básicos para a API.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Criar usuário de teste
        self.user = User.objects.create_user(
            email='teste@exemplo.com',
            password='senha123',
            first_name='Usuário',
            last_name='Teste',
            is_client=True
        )
        
        # Criar um usuário admin
        self.admin = User.objects.create_superuser(
            email='admin@exemplo.com',
            password='admin123',
            first_name='Admin',
            last_name='Teste'
        )
        
        # Criar categoria e subcategoria
        self.categoria = Categoria.objects.create(
            nome='Categoria Teste',
            descricao='Descrição da categoria de teste'
        )
        
        self.subcategoria = SubCategoria.objects.create(
            nome='Subcategoria Teste',
            descricao='Descrição da subcategoria de teste',
            categoria=self.categoria
        )
        
        # Criar anúncio
        self.anuncio = Necessidade.objects.create(
            titulo='Anúncio Teste',
            descricao='Descrição do anúncio de teste',
            cliente=self.user,
            categoria=self.categoria,
            subcategoria=self.subcategoria,
            quantidade=1,
            unidade='un'
        )
        
        # Cliente para testes autenticados
        self.client = APIClient()
    
    def test_listar_categorias_sem_autenticacao(self):
        """
        Teste para verificar se é possível listar categorias sem autenticação.
        """
        url = reverse('categoria-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_criar_categoria_sem_autenticacao(self):
        """
        Teste para verificar se não é possível criar categorias sem autenticação.
        """
        url = reverse('categoria-list')
        data = {
            'nome': 'Nova Categoria',
            'descricao': 'Descrição da nova categoria'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_criar_categoria_com_autenticacao_admin(self):
        """
        Teste para verificar se é possível criar categorias com autenticação de admin.
        """
        self.client.force_authenticate(user=self.admin)
        url = reverse('categoria-list')
        data = {
            'nome': 'Nova Categoria',
            'descricao': 'Descrição da nova categoria'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Categoria.objects.count(), 2)
    
    def test_listar_anuncios_autenticado(self):
        """
        Teste para verificar se é possível listar anúncios com autenticação.
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('necessidade-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_criar_anuncio_autenticado(self):
        """
        Teste para verificar se é possível criar anúncios com autenticação.
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('necessidade-list')
        data = {
            'titulo': 'Novo Anúncio',
            'descricao': 'Descrição do novo anúncio',
            'cliente': self.user.id,
            'categoria': self.categoria.id,
            'subcategoria': self.subcategoria.id,
            'quantidade': 1,
            'unidade': 'un'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Necessidade.objects.count(), 2)
    
    def test_editar_anuncio_proprietario(self):
        """
        Teste para verificar se é possível editar anúncios como proprietário.
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('necessidade-detail', args=[self.anuncio.id])
        data = {
            'titulo': 'Anúncio Editado',
            'descricao': 'Descrição editada',
            'cliente': self.user.id,
            'categoria': self.categoria.id,
            'subcategoria': self.subcategoria.id,
            'quantidade': 2,
            'unidade': 'un'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.anuncio.refresh_from_db()
        self.assertEqual(self.anuncio.titulo, 'Anúncio Editado')
    
    def test_editar_anuncio_nao_proprietario(self):
        """
        Teste para verificar se não é possível editar anúncios como não proprietário.
        """
        # Criar outro usuário
        outro_user = User.objects.create_user(
            email='outro@exemplo.com',
            password='senha123',
            first_name='Outro',
            last_name='Usuário'
        )
        
        self.client.force_authenticate(user=outro_user)
        url = reverse('necessidade-detail', args=[self.anuncio.id])
        data = {
            'titulo': 'Anúncio Editado',
            'descricao': 'Descrição editada',
            'cliente': self.user.id,
            'categoria': self.categoria.id,
            'subcategoria': self.subcategoria.id,
            'quantidade': 2,
            'unidade': 'un'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 