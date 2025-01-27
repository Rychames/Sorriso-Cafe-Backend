from datetime import timedelta
from django.contrib.auth.hashers import check_password, make_password
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from user.models import CustomUser, EmailVerificationCode
from user.tests.test_user_views_base import LoginTestBase, RegisterTestBase

class UserRegisterTest(RegisterTestBase):       
    def advance_time(self, minutes=0, seconds=0):
        current_time = timezone.now()
        new_time = current_time.replace(
            minute=(current_time.minute + minutes) % 60,
            second=(current_time.second + seconds) % 60,
            microsecond=0
        )
        timezone.now = lambda: new_time
        
    def test_create_user_send_email_verify_user_and_complete_register(self):
        """
            Testa o registro de usuário com o fluxo perfeito!
        """
        data = self.default_register_user_data # E-mail e a senha do usuário.      
        response = self.client.post(reverse('user:register-list'), data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertFalse(CustomUser.objects.first().is_active)
        self.assertIn('Código de ativação enviado para o email.', response.data['message'])
        self.assertEqual(EmailVerificationCode.objects.count(), 1)
        
        email = EmailVerificationCode.objects.first()
        response = self.client.post(reverse('user:register-verify-code'), {'email': email.email, 'code': email.code}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Email foi verificado com sucesso!', response.data['message'])
        self.assertTrue(CustomUser.objects.first().is_active)
        
    def test_create_user_send_email_change_password_verify_user_and_complete_register(self):
        """
            Testa o registro de usuário, onde da primeira vez tem uma senha e da segunda tentativa tem uma nova senha!
        """
        data = self.default_register_user_data # E-mail e a senha do usuário.
        
        response = self.client.post(reverse('user:register-list'), data, format='json')
        print(response.content.decode())
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertFalse(CustomUser.objects.first().is_active)
        self.assertTrue(check_password(data['password'], CustomUser.objects.first().password))
        self.assertIn('Código de ativação enviado para o email.', response.data['message'])
        self.assertEqual(EmailVerificationCode.objects.count(), 1)
        
        data2 = {
            'email': data['email'],
            'password': 'newpassword123@',
            'confirm_password': 'newpassword123@'
        }
        print(data2, data)
         
        response = self.client.post(reverse('user:register-list'), data2, format='json')
        print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertFalse(CustomUser.objects.first().is_active)
        self.assertFalse(check_password(data['password'], CustomUser.objects.first().password))
        self.assertTrue(check_password(data2['password'], CustomUser.objects.first().password))
        self.assertIn('Código de ativação enviado para o email.', response.data['message'])
        self.assertEqual(EmailVerificationCode.objects.count(), 1)
        
        email = EmailVerificationCode.objects.first()
        response = self.client.post(reverse('user:register-verify-code'), {'email': email.email, 'code': email.code}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Email foi verificado com sucesso!', response.data['message'])
        self.assertTrue(CustomUser.objects.first().is_active)
    
    def test_create_user_send_email_change_password_verify_user_and_complete_register_wrong_code(self):
        """
            Testa o registro de usuário com o código de ativação errado
        """
        data = self.default_register_user_data # E-mail e a senha do usuário.
        
        response = self.client.post(reverse('user:register-list'), data, format='json')
        print(response.content.decode())
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertFalse(CustomUser.objects.first().is_active)
        self.assertTrue(check_password(data['password'], CustomUser.objects.first().password))
        self.assertIn('Código de ativação enviado para o email.', response.data['message'])
        self.assertEqual(EmailVerificationCode.objects.count(), 1)
        
        email = EmailVerificationCode.objects.first()
        response = self.client.post(reverse('user:register-verify-code'), {'email': email.email, 'code': "111111"}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Código fornecido não é válido.', response.data['message'])
        self.assertFalse(CustomUser.objects.first().is_active)
        
    def test_create_user_with_email_already_used_by_another_user(self):
        """
            Testa a falha ao tentar registrar usuário com EMAIL já existente no banco de dados
        """
        data = self.default_register_user_data
        user = CustomUser.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
        
        response = self.client.post(reverse('user:register-list'), data, format='json')
        self.assertEqual(response.status_code, 400)
        
        self.assertIn('Email já está sendo utilizado por outro usuário.', response.data['error'])    
        self.assertIn('Email em uso. Faça login.', response.data['message'])    
        
    def test_create_user_with_expired_code(self):
        """
            Testa a falha ao tentar registrar usuário com código de ativação expirado
        """
        data = self.default_register_user_data # E-mail e a senha do usuário.
        response = self.client.post(reverse('user:register-list'), data, format='json')
        print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertFalse(CustomUser.objects.first().is_active)
        self.assertIn('Código de ativação enviado para o email.', response.data['message'])
        self.assertEqual(EmailVerificationCode.objects.count(), 1)
        
        code = EmailVerificationCode.objects.first()
        self.assertTrue(code.is_valid())
        
        self.advance_time(minutes=10, seconds=1)
        
        code.refresh_from_db()
        self.assertFalse(code.is_valid())
    
        response = self.client.post(reverse('user:register-verify-code'), {'email': code.email, 'code': code.code}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Código fornecido está expirado. Envie um novo código.', response.data['message'])
        self.assertFalse(CustomUser.objects.first().is_active)    
        
    def test_create_user_with_wrong_email(self):
        """
            Testa a falha ao tentar registrar usuário com EMAIL inválido
        """    
        data = self.default_register_user_data
        data['email'] = 'wrongemail'
        
        response = self.client.post(reverse('user:register-list'), data, format='json')
        self.assertEqual(response.status_code, 400)
        #self.assertIn('Insira um endereço de email válido.', response.data['error']['email'])
        
        data['email'] = 'wrongemail@'
        
        response = self.client.post(reverse('user:register-list'), data, format='json')
        self.assertEqual(response.status_code, 400)
        #self.assertIn('Insira um endereço de email válido.', response.data['error']['email'])
        
        data['email'] = 'wrongemail@.com'
        
        response = self.client.post(reverse('user:register-list'), data, format='json')
        self.assertEqual(response.status_code, 400)
        #self.assertIn('Insira um endereço de email válido.', response.data['error']['email'])
        
        data['email'] = 'wrongemail@garibaldo.com' #### --->> Não existe o dominio garibaldo.com
        
        response = self.client.post(reverse('user:register-list'), data, format='json') 
        self.assertEqual(response.status_code, 200) ### Deve ser 400 pois o email é inválido
        #self.assertIn('Insira um endereço de email válido.', response.data['error']['email'])
        
    def test_create_user_with_wrong_password(self):
        """
            Testa a falha ao tentar registrar usuário com PASSWORD e CONFIRM_PASSWORD diferentes \n
            PASSWORD e CONFIRM_PASSWORD devem ser iguais
        """

        data = self.default_register_user_data
        data['confirm_password'] = 'wrong_password'

        response = self.client.post(reverse('user:register-list'), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('As senhas precisam ser iguais.', response.data['error']['non_field_errors'])

class UserLoginTest(LoginTestBase):
    def test_user_login(self):
        self.create_simple_user()
        user = self.default_login_user_data_simple

        self.assertEqual(CustomUser.objects.count(), 1)

        response = self.client.post(self.login_url, user, format='json')
        print(response.content.decode())
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        
    def test_user_login_invalid_credentials(self):
        login_data = {
            'email': 'wronguser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Credenciais Inválidas.', response.data['error'])

    def test_user_login_inactive_user(self):
        user = self.create_simple_user()
        user.is_active = False
        user.save()
        data = self.default_login_user_data_simple

        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Credenciais Inválidas.', response.data['error'])

    def test_get_and_use_token_refresh_success(self):
        self.create_simple_user()
        data = self.default_login_user_data_simple
        
        login_response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data['data']['refresh']

        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])

    def test_token_refresh_invalid(self):
        invalid_refresh_data = {'refresh': 'invalid_token'}
        response = self.client.post(self.refresh_url, invalid_refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Refresh Token Inválido: O token é inválido ou expirado', response.data['error'])

    def test_token_refresh_missing_refresh_token(self):
        response = self.client.post(self.refresh_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Refresh Token é necessário para esta ação', response.data['error'])

class UserAPITest(LoginTestBase):
    def setUp(self):
        super().setUp()
        self.user = self.create_simple_user()
        
        self.profile_url = reverse('user:profile')  # Ajuste conforme seu basename
        
        # Autentica o usuário
        data = self.default_login_user_data_simple
        login_response = self.client.post(reverse('user:login-list'), data, format='json')
        self.access_token = login_response.data['data']['access']
        self.refresh_token = login_response.data['data']['refresh']
        
    def test_user_api_get_data_authenticated(self):
        """
        Testa o endpoint list (GET) quando o usuário está autenticado.
        """
        response = self.client.get(
            self.profile_url,  # Certifique-se de que a URL corresponde à rota correta
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        print(response.content.decode())  # Apenas para depuração, remova em produção
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Usuário está autenticado.")
        self.assertTrue(response.data['data'])

    def test_user_api_get_data_unauthenticated(self):
        """
        Testa o endpoint list (GET) quando o usuário não está autenticado.
        """
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("As credenciais de autenticação não foram fornecidas.", response.data['error'])

    def test_cannot_create_new_user_via_user_api(self):
        response = self.client.post(
            self.profile_url,  # Certifique-se de que a URL corresponde à rota correta
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        print(response.content.decode())
        #self.assertIn("not allowed", response.content.decode())
        user_count = CustomUser.objects.count()
        self.assertEqual(user_count, 1)  # Ainda deve haver apenas o usuário inicial

    def test_user_api_edit_profile(self):
        # Testa edição do próprio perfil
        update_data = self.default_login_user_data_complete
        update_data['first_name'] = 'Matheus'
        response = self.client.put(self.profile_url, update_data, format='json', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['first_name'], 'Matheus')
        
    def test_user_api_partial_edit_profile(self):
        """
        Testa edição parcial do próprio perfil.
        """
        update_data = {'first_name': 'UpdatedName'}
        response = self.client.patch(
            self.profile_url,  # Verifique se essa URL corresponde à rota correta
            update_data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['first_name'], 'UpdatedName')       
        
    def test_user_api_delete_profile(self):
        """
        Testa exclusão do próprio perfil.
        """
        response = self.client.delete(
            self.profile_url,  # Certifique-se de que a URL corresponde à rota correta
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        print(response.content.decode())  # Apenas para depuração, remova em produção
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(['Usuário deletado!'], response.data['data'])

        # Verifica se o usuário foi realmente deletado
        with self.assertRaises(CustomUser.DoesNotExist):
            self.user.refresh_from_db()
                