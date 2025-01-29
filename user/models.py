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
        

