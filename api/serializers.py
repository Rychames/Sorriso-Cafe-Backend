# api/serializers.py

from turtle import Turtle
from rest_framework import serializers
from api.models import Product, Company, ProductImage
from user.serializers import UserSerializer


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        extra_kwargs = {
            'logo': {'required': False, 'allow_null': True}
        }

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ['product']

class ProductSerializer(serializers.ModelSerializer):
    #images = ProductImageSerializer(many=True, required=False)
    #received_by = serializers.PrimaryKeyRelatedField(read_only=True)

    images = ProductImageSerializer(many=True, required=False)
    received_by = UserSerializer(read_only=True)
    received_company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    current_company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'delivery_man_signature': {'required': False, 'allow_null': True}
        }
    
    def to_representation(self, instance):
        # Serialização: converte IDs para objetos nested
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