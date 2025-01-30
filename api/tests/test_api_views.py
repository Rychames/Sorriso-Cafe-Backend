from django.urls import reverse
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
        for obj in Product.objects.all():
            obj.delete()
        

    def test_create_product(self):
        #print(self.product_data)
        response = self.client.post('/api/products/', self.product_data)
        #print(response.content.decode())
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

    def test_delete_product(self):
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
        
     