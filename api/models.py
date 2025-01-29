# api/models.py

from django.db import models

from user.models import CustomUser

class Company(models.Model):
    logo = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=40)
    address = models.CharField(max_length=300)
      
    #tema (Cor)(Opcional) se não tiver coloca cor padrão
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product', 
        on_delete=models.CASCADE,
        related_name='images'  # ← Adicione related_name para acesso reverso
    )
    image = models.ImageField(upload_to='products/')

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Eletrônicos', 'Eletrônicos'),
        ('Móveis', 'Móveis'),
        ('Alimentos', 'Alimentos'),
        ('Vestuário', 'Vestuário'),
        ('Outros', 'Outros'),
    ]
    
    SIZE_CHOICES = [
        ('S', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=30)
    model = models.CharField(max_length=255)
    company_brand = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.PositiveSmallIntegerField()
    size = models.CharField(choices=SIZE_CHOICES, max_length=1, blank=True, null=True)
    lot = models.BooleanField(default=False)
    sector = models.CharField(max_length=255)
    
    delivered_by = models.CharField(max_length=255)
    delivery_man_signature = models.FileField(upload_to='signatures/', blank=True, null=True)
    
    received_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)
    received_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='received_products'
    )
    date_receipt = models.DateTimeField(auto_now_add=True)
    
    current_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='current_products'
    )

    def __str__(self):
        return self.name