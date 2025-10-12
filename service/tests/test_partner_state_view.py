from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import PartnerState
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser, Shop

class PartnerStateTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PartnerState.as_view()
        # Создаем активного пользователя с ролью продавца
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True, role='seller')
        # Создаем токен для пользователя
        self.access_token = AccessToken.for_user(self.user)
        # Создаем магазин-партнера и ассоциируем его с пользователем
        self.shop = Shop.objects.create(name='Partner Store', user=self.user)

    def test_partner_state_view(self):
        """Тест на успешное изменение состояния магазина партнера"""
        # Данные для изменения состояния магазина
        state_data = {'state': False}
        # Формируем PATCH-запрос с токеном авторизации
        request = self.factory.patch('/api/v1/partner-state/', state_data, format='json')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что состояние магазина изменилось
        updated_shop = Shop.objects.get(pk=self.shop.id)
        self.assertFalse(updated_shop.state)