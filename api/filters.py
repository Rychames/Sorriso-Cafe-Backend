# filters.py
from django_filters import rest_framework as filters
from django.db import models
from .models import Product

class ProductFilter(filters.FilterSet):
    search = filters.CharFilter(method='custom_search', label="Busca geral")
    
    class Meta:
        model = Product
        fields = {
            'name': ['exact', 'icontains'],
            'category': ['exact', 'icontains'],
            'model': ['exact', 'icontains'],
            'company_brand': ['exact', 'icontains'],
            'quantity': ['exact', 'gte', 'lte'],
            'size': ['exact', 'in'],
            'lot': ['exact'],
            'sector': ['exact', 'icontains'],
            'delivered_by': ['exact', 'icontains'],
            'received_company': ['exact'],
            'current_company': ['exact'],
            'date_receipt': ['exact', 'gt', 'lt'],
        }
    
    # Filtros customizados para received_company
    received_company__name = filters.CharFilter(
        field_name='received_company__name',
        lookup_expr='icontains',
        label="Nome da empresa receptora (contém)"
    )
    
    received_company__cnpj = filters.CharFilter(
        field_name='received_company__cnpj',
        lookup_expr='exact',
        label="CNPJ exato da empresa receptora"
    )
    
    received_company__cnpj__icontains = filters.CharFilter(
        field_name='received_company__cnpj',
        lookup_expr='icontains',
        label="CNPJ parcial da empresa receptora"
    )

    # Filtros customizados para current_company
    current_company__name = filters.CharFilter(
        field_name='current_company__name',
        lookup_expr='icontains',
        label="Nome da empresa atual (contém)"
    )
    
    current_company__cnpj = filters.CharFilter(
        field_name='current_company__cnpj',
        lookup_expr='exact',
        label="CNPJ exato da empresa atual"
    )
    
    current_company__cnpj__icontains = filters.CharFilter(
        field_name='current_company__cnpj',
        lookup_expr='icontains',
        label="CNPJ parcial da empresa atual"
    )

    # Mantenha o método custom_search existente
    def custom_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(model__icontains=value) |
            models.Q(company_brand__icontains=value)
        )