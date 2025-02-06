from datetime import timedelta
import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from utils.image_size_validators import compress_image

from .manager import CustomUserManager

class CustomUser(AbstractUser):    
    class UserRoles(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        MODERATOR = 'MODERATOR', 'MODERATOR'
        COMMON = 'COMMON', 'COMMON'

    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    email = models.EmailField(unique=True) 
    role = models.CharField(max_length=30, choices=UserRoles.choices, default=UserRoles.COMMON) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []              
    objects = CustomUserManager()

    def __str__(self):
        return self.email  
    
    def save(self, *args, **kwargs):
        self.username = self.email   
        if self.profile_image: 
            self.profile_image = compress_image(self.profile_image)
            
        self.update_role_based_on_permissions()
            
        super().save(*args, **kwargs)

    def update_role_based_on_permissions(self):
        if self.is_superuser:
            self.role = self.UserRoles.ADMIN
            self.is_staff = True
        elif self.is_staff:
            self.role = self.UserRoles.MODERATOR
        else:
            self.role = self.UserRoles.COMMON

     
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
        

