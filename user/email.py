from datetime import timedelta
import random
import string
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.timezone import now
from user.models import EmailVerificationCode

SEND_EMAIL = True

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))  

def create_verification_code(email):
    try:
        code = EmailVerificationCode.objects.get(email=email)
        if not code.is_valid():
            code.delete()
            raise Exception("Código de verificação precisa ser válido, então será criado um novo código.")
    except:
        code_string = generate_verification_code()
        expires_at = now() + timedelta(minutes=10)  
        code = EmailVerificationCode.objects.create(email=email, code=code_string, expires_at=expires_at)
        
    return code    
     
def send_verification_email(email, code):
    subject = "Gestão de Estoque - Código de Verificação"
    message = f"Seu código de verificação é {code.code}.\nEste código expirará em 10 minutos."
    if SEND_EMAIL:
        send_mail(subject, message, 'almoxarifadogrupopp@gmail.com', [email])

