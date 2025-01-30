from rest_framework import permissions
from api.models import Product, Company, ProductImage
from api.serializers import ProductImageSerializer, ProductSerializer, CompanySerializer
from utils.model_viewset import ModelViewSet
from utils.permissions import IsAuthenticated

class CompanyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]
    
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class ProductViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)
        
class ProductImageViewSet(ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer