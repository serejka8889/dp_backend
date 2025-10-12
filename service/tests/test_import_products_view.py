from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import ImportProductsView
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile

class ImportProductsViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ImportProductsView.as_view()
        # Создаем активного пользователя
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True)
        # Создаем токен для пользователя
        self.access_token = AccessToken.for_user(self.user)
        # Подготавливаем файл для загрузки
        self.file = SimpleUploadedFile('shop1.yaml', '''\
version: 1
goods:
  - id: 1
    name: Смартфон Samsung Galaxy A52
    category: Электроника
    model: SMARTPHONE_SAMSUNG_A52
    price: 29990
    quantity: 10
    shop: Магазин Техносити'''.encode('utf-8'))

    def test_import_products_view(self):
        """Тест на успешный импорт товаров из файла"""
        request = self.factory.post('/api/v1/import-products/', {'file': self.file}, format='multipart')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)