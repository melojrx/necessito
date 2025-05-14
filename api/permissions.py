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