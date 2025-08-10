from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas aos proprietários de um objeto editá-lo.
    """

    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer requisição
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permissões de escrita são permitidas apenas ao proprietário do objeto
        # Assumindo que o objeto tem um atributo 'cliente' ou 'fornecedor' ou 'usuario'
        if hasattr(obj, 'cliente'):
            return obj.cliente == request.user
        elif hasattr(obj, 'fornecedor'):
            return obj.fornecedor == request.user
        elif hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        # Se não tiver nenhum dos atributos acima, verifica se o próprio objeto é o usuário
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
            
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas a administradores editar objetos.
    """

    def has_permission(self, request, view):
        # Permissões de leitura são permitidas para qualquer requisição
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permissões de escrita são permitidas apenas a administradores
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão que permite acesso apenas ao proprietário do objeto ou administradores.
    """

    def has_object_permission(self, request, view, obj):
        # Administradores têm acesso total
        if request.user.is_staff:
            return True
            
        # Proprietários podem acessar seus próprios objetos
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
            
        return False


class UserProfilePermission(permissions.BasePermission):
    """
    Permissão específica para perfis de usuário.
    - Leitura: Todos podem ver perfis públicos
    - Escrita: Apenas o próprio usuário pode editar seu perfil
    - Campos sensíveis: Apenas o próprio usuário ou admin
    """

    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer requisição autenticada
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
            
        # Apenas o próprio usuário pode editar seu perfil
        if request.user == obj:
            return True
            
        # Administradores podem editar qualquer perfil
        if request.user.is_staff:
            return True
            
        return False

    def has_permission(self, request, view):
        # Usuários autenticados podem acessar a API de usuários
        return request.user.is_authenticated


class RestrictSensitiveFields(permissions.BasePermission):
    """
    Permissão para restringir edição de campos sensíveis.
    """
    
    SENSITIVE_FIELDS = [
        'is_staff', 'is_superuser', 'is_active', 'date_joined',
        'email_verified', 'email_verification_token'
    ]
    
    def has_object_permission(self, request, view, obj):
        # Permitir leitura
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Se não está tentando editar campos sensíveis, permitir
        if not any(field in request.data for field in self.SENSITIVE_FIELDS):
            return True
            
        # Apenas administradores podem editar campos sensíveis
        return request.user.is_staff


# === NOVAS PERMISSÕES GRANULARES ===

class NecessidadePermission(permissions.BasePermission):
    """
    Permissões específicas para Necessidades (Anúncios):
    - Leitura: Todos os usuários autenticados podem ver anúncios ativos
    - Criação: Apenas clientes autenticados
    - Edição/Exclusão: Apenas o cliente que criou o anúncio
    """
    
    def has_permission(self, request, view):
        # Usuários devem estar autenticados
        if not request.user.is_authenticated:
            return False
            
        # Para criação, verificar se é cliente
        if request.method == 'POST':
            return request.user.is_client or request.user.is_staff
            
        return True
    
    def has_object_permission(self, request, view, obj):
        # Leitura permitida para todos (se autenticados)
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Edição/exclusão apenas pelo cliente que criou ou admin
        return obj.cliente == request.user or request.user.is_staff


class OrcamentoPermission(permissions.BasePermission):
    """
    Permissões específicas para Orçamentos:
    - Leitura: Apenas o cliente do anúncio e o fornecedor que fez o orçamento
    - Criação: Apenas fornecedores autenticados
    - Edição: Apenas o fornecedor que criou (enquanto não aceito)
    - Exclusão: Apenas o fornecedor que criou ou admin
    """
    
    def has_permission(self, request, view):
        # Usuários devem estar autenticados
        if not request.user.is_authenticated:
            return False
            
        # Para criação, verificar se é fornecedor
        if request.method == 'POST':
            return request.user.is_supplier or request.user.is_staff
            
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admin tem acesso total
        if request.user.is_staff:
            return True
            
        # Leitura: cliente do anúncio ou fornecedor do orçamento
        if request.method in permissions.SAFE_METHODS:
            return (obj.anuncio.cliente == request.user or 
                   obj.fornecedor == request.user)
        
        # Edição/exclusão: apenas o fornecedor que criou
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.fornecedor == request.user
            
        return False


class AvaliacaoPermission(permissions.BasePermission):
    """
    Permissões específicas para Avaliações:
    - Leitura: Todos podem ver avaliações públicas
    - Criação: Apenas usuários que participaram da negociação
    - Edição: Apenas quem criou a avaliação (por tempo limitado)
    - Exclusão: Apenas admin
    """
    
    def has_permission(self, request, view):
        # Leitura permitida para todos autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
            
        # Criação/edição para usuários autenticados
        if request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.is_authenticated
            
        # Exclusão apenas para admin
        if request.method == 'DELETE':
            return request.user.is_staff
            
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin tem acesso total
        if request.user.is_staff:
            return True
            
        # Leitura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Edição apenas pelo usuário que criou
        if request.method in ['PUT', 'PATCH']:
            return obj.usuario == request.user
            
        # Exclusão apenas para admin
        if request.method == 'DELETE':
            return request.user.is_staff
            
        return False


class ChatPermission(permissions.BasePermission):
    """
    Permissões específicas para Chat:
    - Apenas participantes da conversa podem ver/participar
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin tem acesso total
        if request.user.is_staff:
            return True
            
        # Verificar se o usuário é participante da conversa
        # Assumindo que o chat tem campos cliente e fornecedor
        if hasattr(obj, 'cliente') and hasattr(obj, 'fornecedor'):
            return (obj.cliente == request.user or 
                   obj.fornecedor == request.user)
                   
        # Para mensagens, verificar se pertence ao chat do usuário
        if hasattr(obj, 'chat'):
            return (obj.chat.cliente == request.user or 
                   obj.chat.fornecedor == request.user)
                   
        return False


class NotificationPermission(permissions.BasePermission):
    """
    Permissões específicas para Notificações:
    - Usuários só podem ver suas próprias notificações
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin tem acesso total
        if request.user.is_staff:
            return True
            
        # Usuários só podem ver suas próprias notificações
        return obj.user == request.user


class IsOwnerOrRelatedUser(permissions.BasePermission):
    """
    Permissão para objetos que podem ser acessados pelo proprietário
    ou por usuários relacionados (ex: cliente do anúncio pode ver orçamentos)
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin tem acesso total
        if request.user.is_staff:
            return True
            
        # Verificar se é o proprietário direto
        if hasattr(obj, 'usuario') and obj.usuario == request.user:
            return True
        if hasattr(obj, 'cliente') and obj.cliente == request.user:
            return True
        if hasattr(obj, 'fornecedor') and obj.fornecedor == request.user:
            return True
            
        # Para orçamentos, cliente do anúncio também pode ver
        if hasattr(obj, 'anuncio') and hasattr(obj.anuncio, 'cliente'):
            if obj.anuncio.cliente == request.user:
                return True
                
        return False


class ReadOnlyForNonOwners(permissions.BasePermission):
    """
    Permissão que permite leitura para todos, mas escrita apenas para proprietários
    """
    
    def has_object_permission(self, request, view, obj):
        # Leitura permitida para todos autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
            
        # Admin tem acesso total
        if request.user.is_staff:
            return True
            
        # Escrita apenas para proprietários
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        if hasattr(obj, 'cliente'):
            return obj.cliente == request.user
        if hasattr(obj, 'fornecedor'):
            return obj.fornecedor == request.user
            
        return False 