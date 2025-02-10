from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

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
    
class IsNotCommon(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'COMMON':
            response = ResponseData(
                status=401,
                message='Você precisa ter o nível de acesso de um ADMIN ou MODERATOR.',
                error= ["Somente uma conta de nível ADMIN ou MODERATOR consegue acessar."]
                )
            print("usuário não tem permissão")
            raise PermissionDenied(detail=response)
        return True
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.role != 'ADMIN':
            response = ResponseData(
                status=401,
                message='Você precisa ter o nível de acesso de um ADMIN.',
                error= ["Somente uma conta de nível ADMIN consegue acessar."]
                )
            raise PermissionDenied(detail=response)
        return True
    
class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user.role != 'MODERATOR':
            response = ResponseData(
                status=401,
                message='Você precisa ter o nível de acesso de um MODERATOR.',
                error= ["Somente uma conta de nível MODERATOR consegue acessar."]
                )
            raise PermissionDenied(detail=response)
        return True
    
class NotSelf(BasePermission):
    def has_permission(self, request, view):
        if request.user.id == view.kwargs['pk']:
            response = ResponseData(
                status=401,
                message='Você não pode realizar essa ação.',
                error= ["Você não pode realizar essa ação."]
                )
            raise PermissionDenied(detail=response)
        return True

class SelfReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Obtém o ID do usuário autenticado
        user_id = request.user.id
        
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            try:
                request_id = int(view.kwargs.get('pk')) 
            except (KeyError, ValueError):
                #
                return False

            if user_id == request_id:
                print('\nSelf ReadOnly: Acesso negado\n')
                response_data = {
                    'status': 401,
                    'message': 'Você não pode realizar essa ação.',
                    'error': ['Você não pode realizar essa ação.']
                }
                raise PermissionDenied(detail=response_data)

        # Permite o acesso se todas as verificações passarem
        return True