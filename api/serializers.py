from rest_framework import serializers
from users.models import User
from ads.models import Necessidade, AnuncioImagem
from categories.models import Categoria, SubCategoria
from budgets.models import Orcamento
from rankings.models import Avaliacao, AvaliacaoCriterio


class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo User
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'telefone', 
                  'cidade', 'estado', 'is_client', 'is_supplier', 'foto_url']
        read_only_fields = ['id', 'foto_url']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para o modelo User
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'telefone', 
                  'endereco', 'bairro', 'cep', 'cidade', 'estado', 
                  'data_nascimento', 'is_client', 'is_supplier', 'foto_url',
                  'lat', 'lon', 'date_joined']
        read_only_fields = ['id', 'foto_url', 'date_joined']


class SubCategoriaSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo SubCategoria
    """
    class Meta:
        model = SubCategoria
        fields = ['id', 'nome', 'descricao', 'categoria']


class CategoriaSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Categoria
    """
    subcategorias = SubCategoriaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao', 'imagem', 'icone', 'subcategorias']


class AnuncioImagemSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo AnuncioImagem
    """
    class Meta:
        model = AnuncioImagem
        fields = ['id', 'imagem']


class NecessidadeSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Necessidade (Anúncios)
    """
    imagens = AnuncioImagemSerializer(many=True, read_only=True)
    cliente_nome = serializers.SerializerMethodField()
    categoria_nome = serializers.SerializerMethodField()
    subcategoria_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Necessidade
        fields = ['id', 'titulo', 'descricao', 'cliente', 'cliente_nome', 
                  'categoria', 'categoria_nome', 'subcategoria', 'subcategoria_nome',
                  'quantidade', 'unidade', 'status', 'data_criacao', 'imagens']
    
    def get_cliente_nome(self, obj):
        return obj.cliente.get_full_name()
    
    def get_categoria_nome(self, obj):
        return obj.categoria.nome
    
    def get_subcategoria_nome(self, obj):
        return obj.subcategoria.nome


class NecessidadeDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para o modelo Necessidade (Anúncios)
    """
    imagens = AnuncioImagemSerializer(many=True, read_only=True)
    cliente = UserSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    subcategoria = SubCategoriaSerializer(read_only=True)
    
    class Meta:
        model = Necessidade
        fields = '__all__'


class OrcamentoSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Orcamento
    """
    fornecedor_nome = serializers.SerializerMethodField()
    anuncio_titulo = serializers.SerializerMethodField()
    
    class Meta:
        model = Orcamento
        fields = ['id', 'fornecedor', 'fornecedor_nome', 'anuncio', 'anuncio_titulo',
                  'descricao', 'quantidade', 'unidade', 'valor', 'prazo_entrega',
                  'prazo_validade', 'status', 'data_criacao']
    
    def get_fornecedor_nome(self, obj):
        return obj.fornecedor.get_full_name()
    
    def get_anuncio_titulo(self, obj):
        return obj.anuncio.titulo


class AvaliacaoCriterioSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo AvaliacaoCriterio
    """
    criterio_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = AvaliacaoCriterio
        fields = ['id', 'criterio', 'criterio_nome', 'estrelas']
    
    def get_criterio_nome(self, obj):
        return dict(AvaliacaoCriterio.CRITERIO_CHOICES).get(obj.criterio)


class AvaliacaoSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Avaliacao
    """
    criterios = AvaliacaoCriterioSerializer(many=True, read_only=True)
    usuario_nome = serializers.SerializerMethodField()
    avaliado_nome = serializers.SerializerMethodField()
    anuncio_titulo = serializers.SerializerMethodField()
    
    class Meta:
        model = Avaliacao
        fields = ['id', 'usuario', 'usuario_nome', 'avaliado', 'avaliado_nome',
                  'anuncio', 'anuncio_titulo', 'tipo_avaliacao', 'media_estrelas',
                  'data_avaliacao', 'criterios']
    
    def get_usuario_nome(self, obj):
        return obj.usuario.get_full_name()
    
    def get_avaliado_nome(self, obj):
        return obj.avaliado.get_full_name()
    
    def get_anuncio_titulo(self, obj):
        return obj.anuncio.titulo 