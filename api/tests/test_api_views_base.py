from io import BytesIO
from PIL import Image
from rest_framework.test import APITestCase
from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from user.models import CustomUser

class UserDefaultValues:
    email = 'defaultuser@example.com'
    password = 'defaultpassword123'

class LoginTestBase(UserDefaultValues, APITestCase):
    def setUp(self) -> None:   
        self.default_login_user_data_simple = {
            'email': self.email,
            'password': self.password,
        }
        
        self.default_login_user_data_complete = {
            'username': self.email,
            'first_name': "Default",
            'last_name': "User",
            'email': self.email,
            'password': make_password(self.password),
            'is_active': True,
            'is_staff': False,
        }
        
        self.login_url = reverse('user:login-list')
        self.refresh_url = reverse('user:login-refresh')
        
        return super().setUp()
    
    def login(self):
        data = self.default_login_user_data_simple
        login_response = self.client.post(reverse('user:login-list'), data, format='json')
        self.access_token = login_response.data['data']['access']
        self.refresh_token = login_response.data['data']['refresh']
    
    def login_complete(self, role='COMMON'):
        self.user = self.create_simple_user(role=role)
        data = self.default_login_user_data_simple
        login_response = self.client.post(reverse('user:login-list'), data, format='json')
        self.access_token = login_response.data['data']['access']
        self.refresh_token = login_response.data['data']['refresh']
    
    def create_simple_user(self, role='COMMON'):
        user = CustomUser.objects.create(
            email=self.email,
            password=make_password(self.password),
            role=role
        )
        return user
    
    def create_complex_user(self):
        user = CustomUser.objects.create(**self.default_login_user_data_complete)
        return user
    
    def get_test_image(self):
        img = Image.new("RGB", (1024, 1024), color="red")  # Imagem de 1024x1024 pixels
        img_io = BytesIO()
        img.save(img_io, format="JPEG")
        img_io.seek(0)

        # Criação de um arquivo de upload simulado
        return SimpleUploadedFile(
            "test_image.jpg", img_io.read(), content_type="image/jpeg"
        )
        
    def get_simple_test_image(self):
        return SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )
    
    def get_tokens_create_default_user_before(self):
        self.create_simple_user()
        user = self.default_login_user_data_simple
        try:
            response = self.client.post(self.login_url, user, format='json')
            return {'access': response.data['access'], 'refresh': response.data['refresh']}
        except:
            return None
    
    def get_tokens_user(self, user):          
        try:
            response = self.client.post(self.login_url, user, format='json')
            return {'access': response.data['access'], 'refresh': response.data['refresh']}
        except:
            return None
            
class AuthenticatedAPITestBase(LoginTestBase):
    def setUp(self):
        super().setUp()
        self.login_complete()
        self.load_credentials()
        
    def load_credentials(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def clean_credentials(self):
        self.client.credentials()


