from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import PartnerUpdate
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser, Shop
from django.core.files.uploadedfile import SimpleUploadedFile

class PartnerUpdateTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PartnerUpdate.as_view()
        # Создаем активного пользователя с ролью продавца
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True, role='seller')
        # Создаем токен для пользователя
        self.access_token = AccessToken.for_user(self.user)
        # Создаем магазин-партнера и ассоциируем его с пользователем
        self.shop = Shop.objects.create(name='Partner Store', user=self.user)
        # Готовим файл для загрузки (прайс)
        self.file = SimpleUploadedFile('prices.yaml', b'sample content')

    def test_partner_update_view(self):
        """Тест на успешное обновление прайса партнером"""
        # Формируем POST-запрос с токеном авторизации и файлом
        request = self.factory.post('/api/v1/partner-update/', {'file': self.file}, format='multipart')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)