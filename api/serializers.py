from rest_framework import serializers
from django.contrib.auth import authenticate
from dj_rest_auth.serializers import LoginSerializer
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
    valor_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Orcamento
        fields = ['id', 'fornecedor', 'fornecedor_nome', 'anuncio', 'anuncio_titulo',
                  'prazo_entrega', 'prazo_validade', 'observacao', 'tipo_frete', 
                  'valor_frete', 'forma_pagamento', 'condicao_pagamento', 
                  'tipo_venda', 'status', 'data_criacao', 'valor_total']
        read_only_fields = ['id', 'data_criacao', 'valor_total']
    
    def get_fornecedor_nome(self, obj):
        return obj.fornecedor.get_full_name()
    
    def get_anuncio_titulo(self, obj):
        return obj.anuncio.titulo
    
    def get_valor_total(self, obj):
        return str(obj.valor_total())


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

# === SERIALIZERS ESPECÍFICOS PARA DOCUMENTAÇÃO ===

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer para alteração de senha
    """
    old_password = serializers.CharField(
        max_length=128,
        help_text="Senha atual do usuário",
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        max_length=128,
        help_text="Nova senha (deve conter pelo menos 8 caracteres, incluindo letras e números)",
        style={'input_type': 'password'}
    )

    class Meta:
        examples = {
            'Exemplo de alteração de senha': {
                'old_password': 'senha_atual_123',
                'new_password': 'nova_senha_456'
            }
        }


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer para respostas de erro padronizadas
    """
    error = serializers.CharField(help_text="Descrição do erro")
    details = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Detalhes adicionais do erro"
    )

    class Meta:
        examples = {
            'Erro de validação': {
                'error': 'Dados inválidos',
                'details': ['Este campo é obrigatório.']
            },
            'Erro de permissão': {
                'error': 'Você não tem permissão para realizar esta ação.'
            }
        }


class SuccessResponseSerializer(serializers.Serializer):
    """
    Serializer para respostas de sucesso padronizadas
    """
    message = serializers.CharField(help_text="Mensagem de sucesso")

    class Meta:
        examples = {
            'Operação bem-sucedida': {
                'message': 'Operação realizada com sucesso.'
            }
        }


class PaginationResponseSerializer(serializers.Serializer):
    """
    Serializer para respostas paginadas
    """
    count = serializers.IntegerField(help_text="Total de itens")
    next = serializers.URLField(allow_null=True, help_text="URL da próxima página")
    previous = serializers.URLField(allow_null=True, help_text="URL da página anterior")
    results = serializers.ListField(help_text="Lista de resultados da página atual")

    class Meta:
        examples = {
            'Resposta paginada': {
                'count': 25,
                'next': 'http://api.indicai.com.br/api/v1/users/?page=3',
                'previous': 'http://api.indicai.com.br/api/v1/users/?page=1',
                'results': []
            }
        }


class VersionInfoSerializer(serializers.Serializer):
    """
    Serializer para informações de versão da API
    """
    version = serializers.CharField(help_text="Versão da API")
    status = serializers.CharField(help_text="Status da versão (stable, deprecated, etc.)")
    description = serializers.CharField(help_text="Descrição da versão")
    release_date = serializers.DateField(help_text="Data de lançamento")
    features = serializers.ListField(
        child=serializers.CharField(),
        help_text="Lista de funcionalidades da versão"
    )

    class Meta:
        examples = {
            'Informações da versão v1': {
                'version': 'v1',
                'status': 'stable',
                'description': 'Primeira versão estável da API do Indicai',
                'release_date': '2025-01-20',
                'features': [
                    'Autenticação JWT',
                    'CRUD de usuários',
                    'Gestão de categorias e subcategorias'
                ]
            }
        }


# === SERIALIZERS EXPANDIDOS PARA DOCUMENTAÇÃO ===

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de usuários via registro
    """
    password1 = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="Senha do usuário",
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        max_length=128,
        write_only=True,
        help_text="Confirmação da senha",
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'telefone', 'password1', 'password2']
        extra_kwargs = {
            'email': {'help_text': 'Endereço de e-mail único do usuário'},
            'first_name': {'help_text': 'Nome do usuário'},
            'last_name': {'help_text': 'Sobrenome do usuário'},
            'telefone': {'help_text': 'Número de telefone com DDD'},
        }

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs


class CustomLoginSerializer(LoginSerializer):
    """
    Serializer customizado para login usando apenas email e senha
    """
    username = None  # Remove o campo username
    email = serializers.EmailField(
        required=True,
        help_text="E-mail do usuário cadastrado no sistema"
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        help_text="Senha do usuário"
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )

            if not user:
                msg = 'Credenciais inválidas.'
                raise serializers.ValidationError(msg, code='authorization')

            if not user.is_active:
                msg = 'Conta de usuário desabilitada.'
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = 'É necessário fornecer email e senha.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class LoginRequestSerializer(serializers.Serializer):
    """
    Serializer para documentar o request body do login
    """
    email = serializers.EmailField(
        required=True,
        help_text="E-mail do usuário cadastrado no sistema"
    )
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        help_text="Senha do usuário"
    )

    class Meta:
        examples = {
            'login_example': {
                'summary': 'Exemplo de Login',
                'description': 'Exemplo de dados para realizar login',
                'value': {
                    'email': 'usuario@exemplo.com',
                    'password': 'minha_senha_123'
                }
            }
        }

class LoginResponseSerializer(serializers.Serializer):
    """
    Serializer para documentar a resposta do login
    """
    access = serializers.CharField(help_text="Token de acesso JWT (válido por 1 hora)")
    refresh = serializers.CharField(help_text="Token de refresh JWT (válido por 7 dias)")
    user = UserDetailSerializer(help_text="Dados do usuário autenticado")

    class Meta:
        examples = {
            'login_success': {
                'summary': 'Login realizado com sucesso',
                'description': 'Resposta quando o login é realizado com sucesso',
                'value': {
                    'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                    'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                    'user': {
                        'id': 1,
                        'email': 'usuario@exemplo.com',
                        'first_name': 'João',
                        'last_name': 'Silva',
                        'tipo_usuario': 'cliente'
                    }
                }
            }
        }


# === MELHORAR SERIALIZERS EXISTENTES ===

class NecessidadeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de necessidades com validações detalhadas
    """
    class Meta:
        model = Necessidade
        fields = ['titulo', 'descricao', 'categoria', 'subcategoria', 'quantidade', 'unidade']
        extra_kwargs = {
            'titulo': {
                'help_text': 'Título claro e descritivo da necessidade (máx. 200 caracteres)',
                'max_length': 200
            },
            'descricao': {
                'help_text': 'Descrição detalhada do que você precisa, incluindo especificações técnicas se necessário',
                'style': {'base_template': 'textarea.html'}
            },
            'categoria': {
                'help_text': 'Categoria principal do produto/serviço necessário'
            },
            'subcategoria': {
                'help_text': 'Subcategoria específica para melhor classificação'
            },
            'quantidade': {
                'help_text': 'Quantidade necessária (número inteiro positivo)',
                'min_value': 1
            },
            'unidade': {
                'help_text': 'Unidade de medida (ex: un, kg, m², horas, etc.)',
                'max_length': 20
            }
        }

    def validate_titulo(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("O título deve ter pelo menos 10 caracteres.")
        return value.strip()

    def validate_descricao(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError("A descrição deve ter pelo menos 20 caracteres.")
        return value.strip()


class OrcamentoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de orçamentos com validações detalhadas
    """
    class Meta:
        model = Orcamento
        fields = [
            'anuncio', 'prazo_entrega', 'prazo_validade', 'observacao',
            'tipo_frete', 'valor_frete', 'forma_pagamento', 'condicao_pagamento', 'tipo_venda'
        ]
        extra_kwargs = {
            'anuncio': {
                'help_text': 'ID da necessidade para a qual você está fazendo o orçamento'
            },
            'prazo_entrega': {
                'help_text': 'Prazo para entrega/execução do serviço (em dias)'
            },
            'prazo_validade': {
                'help_text': 'Prazo de validade do orçamento (em dias)'
            },
            'observacao': {
                'help_text': 'Observações adicionais sobre o orçamento',
                'style': {'base_template': 'textarea.html'}
            },
            'tipo_frete': {
                'help_text': 'Tipo de frete (ex: CIF, FOB, Por conta do cliente)'
            },
            'valor_frete': {
                'help_text': 'Valor do frete em reais (se aplicável)'
            },
            'forma_pagamento': {
                'help_text': 'Forma de pagamento aceita (ex: Dinheiro, PIX, Cartão)'
            },
            'condicao_pagamento': {
                'help_text': 'Condições de pagamento (ex: À vista, 30 dias, Parcelado)'
            },
            'tipo_venda': {
                'help_text': 'Tipo de venda (ex: Produto, Serviço, Produto + Instalação)'
            }
        } 