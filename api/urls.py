from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name="api"


router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'companies', views.CompanyViewSet)
router.register(r'product-images', views.ProductImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

'''

from django.urls import path
from .views import ProductCreateView

urlpatterns = [
    path('inventory/', ProductCreateView.as_view(), name='product-create'),
]
'''