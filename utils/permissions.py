from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated

from utils.responses import ResponseData


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        if not is_authenticated:
            response = ResponseData(
                status=401,
                message='Você precisa validar suas credenciais.',
                error= ["As credenciais de autenticação não foram fornecidas."]
                )
            raise NotAuthenticated(detail=response)
        return is_authenticated
    
