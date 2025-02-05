from rest_framework import permissions
from api.filters import ProductFilter
from api.models import Product, Company, ProductImage
from api.serializers import ProductImageSerializer, ProductSerializer, CompanySerializer
from utils.model_viewset import ModelViewSet
from utils.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class CompanyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]

class ProductViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.select_related('received_company', 'current_company')
    serializer_class = ProductSerializer
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)
        
class ProductImageViewSet(ModelViewSet):
    #permission_classes = [IsAuthenticated]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer