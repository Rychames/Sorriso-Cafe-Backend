# api/views.py

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from api.models import Product, Company, ProductImage
from api.serializers import ProductImageSerializer, ProductSerializer, CompanySerializer
from utils.model_viewset import ModelViewSet

class CompanyViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class ProductViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)
        
class ProductImageViewSet(ModelViewSet):
    #permission_classes = [AllowAny]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer