# api/models.py

from django.db import models

from user.models import CustomUser
from utils.image_size_validators import compress_image

class Company(models.Model):
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=40)
    address = models.CharField(max_length=300)
    
    industry = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name

    @property
    def products_count(self):
        """
        Retorna o número de produtos associados a esta empresa.
        """
        return self.current_products.count()  

    def save(self, *args, **kwargs):
        #if self.logo:  # Comprime apenas se houver imagem
        #    self.logo = compress_image(self.logo)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product', 
        on_delete=models.CASCADE,
        related_name='images'  # ← Adicione related_name para acesso reverso
    )
    image = models.ImageField(upload_to='products/')
    
    def save(self, *args, **kwargs):
        #if self.image:  # Comprime apenas se houver imagem
        #    self.image = compress_image(self.image)
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)

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
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    lot = models.BooleanField(default=False)
    sector = models.CharField(max_length=255)
    
    last_transporter_name =  models.CharField(max_length=255, blank=True, null=True)
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
    
    def delete(self, *args, **kwargs):
        for product_image in self.images.all():
            product_image.delete()  
        super().delete(*args, **kwargs) 
    
   