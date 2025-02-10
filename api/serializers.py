# api/serializers.py

from turtle import Turtle
from django.db.models import DecimalField
from rest_framework import serializers
from api.models import Product, Company, ProductImage
from user.serializers import UserSerializer

class APISerializer(serializers.ModelSerializer):
    """
    Ajusta os campos Decimais para não se tornar String no Serializer
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  
        for field_name, field in self.fields.items():
            if isinstance(self.Meta.model._meta.get_field(field_name), DecimalField):
                self.fields[field_name] = serializers.DecimalField(
                    max_digits=field.max_digits,
                    decimal_places=field.decimal_places,
                    coerce_to_string=False
                )

class CompanySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)  

    class Meta:
        model = Company
        fields = '__all__'
 
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ['product']

class ProductSerializer(APISerializer):
    images = ProductImageSerializer(many=True, required=False)
    received_by = UserSerializer(read_only=True)
    received_company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    current_company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'delivery_man_signature': {'required': False, 'allow_null': True},
            'price': {'required': False, 'allow_null': True}
        }
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['received_company'] = CompanySerializer(instance.received_company).data
        representation['current_company'] = CompanySerializer(instance.current_company).data
        return representation

    def create(self, validated_data):
        images_data = self.context.get('request').FILES.getlist('images') 
        validated_data['received_by'] = self.context['request'].user
        product = Product.objects.create(**validated_data)
        
        for image_data in images_data:
            ProductImage.objects.create(product=product, image=image_data)
            
        return product
    
