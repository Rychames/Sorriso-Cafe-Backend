from django.contrib.auth import authenticate
from django.http import FileResponse
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.model_viewset import ModelViewSet
from utils.responses import Response, StrResponse
from utils.permissions import IsAuthenticated, IsModerator, IsNotCommon
from user.email import create_verification_code, send_verification_email
from user.serializers import (
    LoginUserSerializer, 
    RegisterUserSerializer,
    UserManagerSerializer, 
    VerifyCodeSerializer, 
    UserSerializer
)   
from user.models import CustomUser, EmailVerificationCode

class UserRegisterViewSet(viewsets.ViewSet):
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Registro de usuário.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password'],
            properties={
                'email':openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, title="Email", default="example@gmail.com"),
                'password':openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, title="Senha", min_lenght=8),
                'confirm_password':openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, title="Confirmação de Senha", min_lenght=8),
            },
        ),
        responses={           
            '200': StrResponse(data="Valide sua conta através do código enviado por email.", message="Código de ativação enviado para o email.", status=200),
            '400': StrResponse(error="...", message="Não foi possível registrar o usuário.", status=400),  
            '409': StrResponse(error=["Email já está sendo utilizado por outro usuário."], message="Email em uso. Faça login.", status=400),
            '500': StrResponse(error="...", message="Email não enviado.", status=500),
        }
    )
    def create(self, request, *args, **kwargs):             
        try:
            email = request.data.get('email')
            user = CustomUser.objects.get(email=email)
            if user.is_active:
                return Response(error=["Email já está sendo utilizado por outro usuário."], message="Email em uso. Faça login.", status=400)
            serializer = RegisterUserSerializer(data=request.data, instance=user)           
        except:
            serializer = RegisterUserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.set_password(request.data.get('password'))
            user.save()
           
            try:
                code = create_verification_code(email)
                send_verification_email(email, code)
            except Exception as e:
                return Response(
                    error=e,
                    message="Email não enviado.",
                    status=400
                )   
            return Response(data="Valide sua conta através do código enviado por email.", message="Código de ativação enviado para o email.", status=status.HTTP_200_OK)
        return Response(error=serializer.errors, message="Não foi possível registrar o usuário.", status=status.HTTP_400_BAD_REQUEST)   

    @swagger_auto_schema(
        request_body=VerifyCodeSerializer,
        responses={
            200: StrResponse(data=['Email verificado!'], message="Email foi verificado com sucesso!", status=200),
            400: StrResponse(error=["Código inválido"], message="Código fornecido não é válido.", status=400),
            400: StrResponse(error=["Código expirado"], message="Código fornecido está expirado. Envie um novo código.", status=400),
            422: StrResponse(error=["Email inválido."], message="Email fornecido não é válido.", status=422),
    })
    @action(detail=False, methods=['post'], url_path='verify-code', url_name='verify-code')
    def verify_code(self, request): 
        email = request.data.get('email')
        code = request.data.get('code')

        if not email:
            return Response(error={email: "Campo email é obrigatório."}, status=422)
        if not code:
            return Response(error={code: "Campo code é obrigatório."}, status=422)

        try:
            verification_code = EmailVerificationCode.objects.get(email=email)
            
            if verification_code.code == code:
                if verification_code.is_valid():
                    verification_code.activated = True
                    verification_code.save()
                    user = CustomUser.objects.get(email=email)
                    user.is_active = True
                    user.save()
                    return Response(data=['Email verificado!'], message="Email foi verificado com sucesso!", status=200)
                return Response(error=["Código expirado"], message="Código fornecido está expirado. Envie um novo código.", status=400)
            return Response(error=["Código inválido"], message="Código fornecido não é válido.", status=400)
        
        except EmailVerificationCode.DoesNotExist:
            return Response(error=["Email inválido."], message="Email fornecido não é válido.", status=422)

class UserLoginViewSet(viewsets.ViewSet):
    serializer_class = LoginUserSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email':openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, title="Email", min_lenght=8, default="math@gmail.com"),
                'password':openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, title="Senha", min_lenght=8, default="123"),
                'confirm_password':openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, title="Confirmação de Senha", min_lenght=8, default="123"),
            },
        ),
        responses={
            200: StrResponse(
                data={
                    'access': "access",
                    'refresh': "refresh",
                },
                message=f"Login concluído! Seja bem-vindo (user email)!",
                status=200,
            ),
            400: StrResponse(
                status=400,
                error=['Email e Senha são obrigatórios.'],
                message="Não é possível fazer login sem Email ou Senha.",
            ),
            400: StrResponse(
                status=400,
                error=["Credenciais Inválidas."],
                message=f"Não foi possível fazer login, usuário não encontrado.",
            ),
        },
    )
    def create(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                status=400,
                error=['Email e Senha são obrigatórios.'],
                message="Não é possível fazer login sem Email ou Senha.",
            )

        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response(
                data={
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                message=f"Login concluído! Seja bem-vindo {user}!",
                status=200,
            )
        else:
            return Response(
                status=400,
                error=["Credenciais Inválidas."],
                message=f"Não foi possível fazer login, usuário não encontrado.",
            )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh':openapi.Schema(type=openapi.TYPE_STRING, title="Refresh Token"),
            },
        ),
        responses={
            201: openapi.Response(
                description="Novos Tokens.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='New Access token',),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='New Refresh token',)
                    }
                ),
                examples={
                    'application/json': {
                        "access": 'NEW_TOKEN_ACCESS',
                        "refresh": "NEW_TOKEN_REFRESH",
                    }
                }
            )
        }                                        
    )
    @action(detail=False, methods=['post'], url_path='refresh', url_name='refresh')
    def refresh_token(self, request):
        """
        Realiza a autenticação com o refresh_token e retorna novos tokens.
        """
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                error=['Refresh Token é necessário para esta ação'],
                message='Não é possível renovar seu login sem um Refresh Token.',
                status=400,
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response(
                data={
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                message=f"Seu login foi renovado! Seja bem-vindo de novo!",
                status=200,
            )

        except Exception as e:
            return Response(
                error=[f"Refresh Token Inválido: {str(e)}"],
                message=f"Não foi possível renovar seu login.",
                status=400,
            )          

class UserManagerViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserManagerSerializer
    queryset = CustomUser.objects.all()
    http_method_names = ['get', 'put', 'patch', 'delete']  

class UserAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        responses={
            200: StrResponse(
                data="{User Data}",
                message="Usuário está autenticado.",
                status=200,
            ),            
            401: StrResponse(
                error=["Usuário não está autenticado."],
                message="Usuário precisa está autenticado para acessar esta área.",
                status=401,
            )
        },
        security=[{'Bearer': []}]
    )
    def get(self, request):
        """
        Retorna os dados do usuário autenticado.
        """
        user = request.user

        if user.is_authenticated:            
            return Response(
                data=UserSerializer(user).data,
                message="Usuário está autenticado.",
                status=200,
            )
        return Response(
                error=["Usuário não está autenticado."],
                message="Usuário precisa está autenticado para acessar esta área.",
                status=401,
            )
        
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            200: StrResponse(
                status=200,
                data="User Data",
                message="Usuário atualizado com sucesso!",
            ),
            400: StrResponse(
                data="...",
                message="Usuário não foi atualizado com sucesso.",
                status=400,
            )
        },
        security=[{'Bearer': []}]
    )
    def put(self, request):
        user = request.user
        print(user.first_name)
        serializer = UserSerializer(instance=user, data=request.data, partial=False)
        if serializer.is_valid():
            user = serializer.save()
            print(user.first_name)
            return Response(
                data=serializer.data,
                message="Usuário atualizado com sucesso!",
                status=200,
            )
        return Response(
                data=serializer.errors,
                message="Usuário não foi atualizado com sucesso.",
                status=400,
            )

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            200: StrResponse(data="User Data", message="Usuário foi atualizado com sucesso!", status=200),
            400: StrResponse(error="...", message="Usuário não foi atualizado com sucesso.", status=400),
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()

            return Response(
                    data=serializer.data,
                    message="Usuário foi atualizado com sucesso!",
                    status=200,
                )
        return Response(
                error=serializer.errors,
                message="Usuário não foi atualizado com sucesso.",
                status=400,
            )

    @swagger_auto_schema(
        responses={
            200: StrResponse(
                data=['Usuário deletado!'],
                message="Usuário foi possível deletado com sucesso!",
                status=200,
            ),
            400: StrResponse(
                error=['Usuário não deletado.'],
                message="Não foi possível deletar o usuário",
                status=400,
            )
        },
        security=[{'Bearer': []}]
    )
    def delete(self, request):
        user = request.user
        if user is not None:
            user.delete()
            return Response(
                data=['Usuário deletado!'],
                message="Usuário foi possível deletado com sucesso!",
                status=200,
            )
        return Response(
                error=['Usuário não deletado.'],
                message="Não foi possível deletar o usuário",
                status=400,
            )

class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            if user.profile_image:
                return FileResponse(user.profile_image.open('rb'), content_type='image/jpeg')
            else:
                return Response({"detail": "No profile image found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": e}, status=status.HTTP_404_NOT_FOUND)
    