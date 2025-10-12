from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import ExportProductsView
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser

class ExportProductsViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ExportProductsView.as_view()
        # Создаем активного пользователя
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True)
        # Создаем токен для пользователя
        self.access_token = AccessToken.for_user(self.user)

    def test_export_products_view(self):
        """Тест на успешный экспорт товаров в файл"""
        request = self.factory.post('/api/v1/export-products/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)