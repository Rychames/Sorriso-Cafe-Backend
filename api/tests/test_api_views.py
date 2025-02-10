from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import Company, Product, ProductImage
from .test_api_views_base import AuthenticatedAPITestBase
from website.settings import BASE_DIR

class CompanyTests(AuthenticatedAPITestBase):
    def setUp(self):
        super().setUp()
        self.company_data = {
            'logo': None,
            'name': 'Empresa Teste',
            'cnpj': '00.000.000/0001-00',
            'address': 'Rua Teste, 123',
        }
        self.test_company = Company.objects.create(**self.company_data)
        self.url = reverse('api:company-list')

    def get_image(self):
        return SimpleUploadedFile(
            name='test_image.jpg', 
            content=open(rf'{BASE_DIR}\media\products\test.jpg', 'rb').read(), 
            content_type='image/png'
        )

    def tearDown(self):
        self.test_company.logo.delete()
        self.test_company.delete()

    def test_create_company(self):
        response = self.client.post(
            self.url,
            {
                **self.company_data,
                'cnpj': '11.111.111/0001-11',
                'logo': self.get_image()
            },
            format='multipart'
        )
        print(response.content.decode())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Company.objects.count(), 2)
        print(Company.objects.last().logo)
        self.assertIsNotNone(Company.objects.last().logo)

    def test_retrieve_company(self):
        detail_url = reverse('api:company-detail', args=[self.test_company.id])
        response = self.client.get(detail_url)
        print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['name'], 'Empresa Teste')

    def test_update_company(self):
        detail_url = reverse('api:company-detail', args=[self.test_company.id])
        updated_data = {
            'name': 'Empresa Atualizada',
            'cnpj': '11.000.000/0001-00',
            'address': 'Nova Rua, 456'
        }
        response = self.client.patch(detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.test_company.refresh_from_db()
        self.assertEqual(self.test_company.name, 'Empresa Atualizada')

    def test_delete_company(self):
        detail_url = reverse('api:company-detail', args=[self.test_company.id])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Company.objects.count(), 0)

class ProductTests(AuthenticatedAPITestBase):
    def setUp(self):
        super().setUp()
        self.company_data = {
            'logo': None,
            'name': 'Empresa Teste',
            'cnpj': '00.000.000/0001-00',
            'address': 'Rua Teste, 123',
        }
        self.company = Company.objects.create(**self.company_data)
        
        self.product_data = {
            'name': 'Mouse',
            'category': 'Eletrônicos',
            'model': 'Storm',
            'company_brand': 'Redragon',
            'description': '12.000 de DPI',
            'quantity': 2,
            'size': 'S',
            'price': 100.00,
            'lot': False,
            'sector': 'Informática',
            'delivered_by': 'Mercado Livre',
            'images': [
                self.get_image(),
                self.get_image(),
                #self.get_image(),
            ],
            'received_company': self.company.id,
            'current_company': self.company.id,
        }        
    
    def get_image(self):
        return SimpleUploadedFile(
            name='test_image.jpg', 
            content=open(rf'{BASE_DIR}\media\products\test.jpg', 'rb').read(), 
            content_type='image/png'
        )
        
    def tearDown(self):
        self.company.logo.delete()
        for obj in ProductImage.objects.all():
            obj.image.delete()
            obj.delete()
        for obj in Product.objects.all():
            obj.delete()
    
    def test_create_product_without_price(self):
        data = self.product_data.copy()
        data.pop('price')
        response = self.client.post('/api/products/', data)
        print(response.content.decode())
        self.assertEqual(response.status_code, 201)

    def test_create_product(self):
        #print(self.product_data)
        response = self.client.post('/api/products/', self.product_data)
        print(response.content.decode())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, 'Mouse')
        print(ProductImage.objects.first())
        print(Product.objects.first().images.all().count())
        self.assertEqual(Product.objects.first().images.all().count(), ProductImage.objects.count())

    def test_list_products(self):
        self.test_create_product()
        response = self.client.get('/api/products/')
        #print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])


    def test_list_products_not_authenticated(self):
        self.test_create_product()
        self.clean_credentials()
        response = self.client.get('/api/products/')
        print(response.content.decode())
        self.assertEqual(response.status_code, 401)

    def test_retrieve_product(self):
        self.test_create_product()
        product = Product.objects.first()
        response = self.client.get(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['name'], 'Mouse')

    def test_update_product(self):
        self.test_create_product()
        product = Product.objects.first()
        
        updated_data = self.product_data.copy()
        updated_data['quantity'] = 20
        response = self.client.put(f'/api/products/{product.id}/', updated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.get().quantity, 20)

    def test_delete_product(self): #não deleta imagens
        self.test_create_product()
        product = Product.objects.first()
        
        response = self.client.delete(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)
        
    def test_retrieve_product_images(self):  
        self.test_create_product()
        product = Product.objects.first()
        response = self.client.get(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, 200)
        print(response.content.decode())
        self.assertEqual(response.data['data']['images'][0]['id'], 1)
        self.assertEqual(response.data['data']['images'][1]['id'], 2)
        
    def create_test_products(self):
        """Cria produtos de teste com diferentes características"""
        company2 = Company.objects.create(
            name="Armazém Central",
            cnpj="11.111.111/0001-11",
            address="Av. Principal, 1000"
        )

        products = [
            {
                'name': 'Teclado Mecânico',
                'category': 'Eletrônicos',
                'quantity': 15,
                'size': 'M',
                'received_company': self.company,
                'current_company': company2,
                'company_brand': 'Redragon'
            },
            {
                'name': 'Cadeira Gamer',
                'category': 'Móveis',
                'quantity': 5,
                'size': 'G',
                'received_company': company2,
                'current_company': self.company,
                'company_brand': 'DXRacer'
            },
            {
                'name': 'Mouse Pad Grande',
                'category': 'Acessórios',
                'quantity': 30,
                'size': 'G',
                'received_company': self.company,
                'current_company': self.company,
                'company_brand': 'Logitech'
            }
        ]

        for prod in products:
            product = Product.objects.create(**prod)
            # Adiciona imagens para testar o relacionamento
            ProductImage.objects.create(product=product, image=self.get_image())

        return company2

    # Testes de filtros
    def test_filter_by_name_icontains(self):
        self.create_test_products()
        response = self.client.get('/api/products/?name__icontains=Mecânico')
        self.assertEqual(response.status_code, 200)
        print(response.content.decode())
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Teclado Mecânico')

    def test_filter_by_category_exact(self):
        self.create_test_products()
        response = self.client.get('/api/products/?category=Móveis')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Cadeira Gamer')

    def test_filter_by_quantity_range(self):
        self.create_test_products()
        response = self.client.get('/api/products/?quantity__gte=10&quantity__lte=20')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Teclado Mecânico')

    def test_filter_by_received_company_name(self):
        company2 = self.create_test_products()
        response = self.client.get(f'/api/products/?received_company__name={self.company.name}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 2)

    def test_filter_by_current_company_cnpj(self):
        company2 = self.create_test_products()
        response = self.client.get(f'/api/products/?current_company__cnpj={company2.cnpj}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 1)

    def test_custom_search_filter(self):
        self.create_test_products()
        # Deve encontrar em name, description, model ou company_brand
        response = self.client.get('/api/products/?search=Logitech')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Mouse Pad Grande')

    def test_filter_combinations(self):
        self.create_test_products()
        response = self.client.get(
            '/api/products/?category=Eletrônicos&size=M&quantity__gte=10'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], 'Teclado Mecânico')

