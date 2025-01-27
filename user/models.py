from datetime import timedelta
import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .manager import CustomUserManager

class CustomUser(AbstractUser):    
    email = models.EmailField(unique=True) 
    #full_name = models.CharField(max_length=255)
    #companies = models.ManyToManyField('Company', blank=True)
    #profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []              
    objects = CustomUserManager()

    def __str__(self):
        return self.email  
    
    def save(self, *args, **kwargs):
        self.username = self.email   
        super().save(*args, **kwargs)

       
'''
class Company(models.Model):
    #logo = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=40)
    address = models.CharField(max_length=300)
    #tema (Cor)(Opcional) se não tiver coloca cor padrão


class Product(models.Model):
    CATEGORYS_CHOICES = [
        ('Eletrônicos', 'Eletrônicos'),
        ('Móveis', 'Móveis'),
        ('Alimentos', 'Alimentos'),
        ('Vertuário', 'Vertuário'),
        ('Outros', 'Outros'),
    ]
    SIZE_CHOICES = [
        ('S', 'S'),
        ('M', 'M'),
        ('G', 'G'),
    ]
    
    name = models.CharField(max_length=255)
    category = models.CharField(choices=CATEGORYS_CHOICES, max_length=30)
    model = models.CharField(max_length=255)
    company_brand = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    quantity = models.PositiveSmallIntegerField()
    size = models.CharField(choices=SIZE_CHOICES, max_length=30)
    lot = models.BooleanField(default=False)
    
    delivered_by = models.CharField(max_length=255)
    received_by = models.CharField(max_length=255)
    date_receipt = models.DateTimeField()
    
    company = models.ForeignKey('Company')
    
    
@EntradaDeProdutos
produto = @Produto

Quem entregou
Data e hora de recebimento
assinatura do responsável (Arquivo.pdf)

@SaídaDeProdutos
produto = @Produto

Quem retirou
Data e hora de saída
Destino do material
assinatura (Arquivo.pdf)

    '''
     
class EmailVerificationCode(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)  # Código de 6 dígitos
    created_at = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    def is_valid(self):
        return timezone.now() < self.expires_at

    def save(self, *args, **kwargs):
        self.code = ''.join(random.choices(string.digits, k=6))  
        self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)  
        

