from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.transaction import commit
from django.urls import reverse
from rest_framework.test import APITestCase
from user.models import CustomUser, EmailVerificationCode
from io import BytesIO
from PIL import Image

class UserDefaultValues:
    email = 'defaultuser@example.com'
    password = 'defaultpassword123'

class RegisterTestBase(UserDefaultValues, APITestCase):
    def setUp(self) -> None:       
        self.default_register_user_data = {
            'email': self.email,
            'password': self.password,
            'confirm_password': self.password
        }
        return super().setUp()
        
    def create_email_code(self, override_activation=True):
        email_field = self.default_register_user_data.get('email')
        email = EmailVerificationCode.objects.create(email=email_field)
        email.activated = override_activation
        email.save()
        return email

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
            #'profile_image': self.get_test_image(),
            'email': self.email,
            'password': make_password(self.password),
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            #'date_birth': '1990-01-01',
            #'phone_number': '123456789'
        }
        
        self.login_url = reverse('user:login-list')
        self.refresh_url = reverse('user:login-refresh')
        
        return super().setUp()
    
    def login_complete(self):
        self.user = self.create_simple_user()
        data = self.default_login_user_data_simple
        login_response = self.client.post(reverse('user:login-list'), data, format='json')
        self.access_token = login_response.data['data']['access']
        self.refresh_token = login_response.data['data']['refresh']
    
    def create_simple_user(self):
        user = CustomUser.objects.create(
            username=self.email,
            email=self.email,
            password=make_password(self.password),
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
            
class AuthTestBase(RegisterTestBase, LoginTestBase):
    pass
