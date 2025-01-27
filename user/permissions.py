from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada que permite que um usuário acesse ou modifique seus próprios dados,
    ou permite acesso a um administrador (dono).
    """

    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário é o dono ou se é um administrador
        if request.user == obj or request.user.is_staff:
            return True
        return False
