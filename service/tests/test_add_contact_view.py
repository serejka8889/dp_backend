from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import AddContactView
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser  # Кастомная модель пользователя

class AddContactViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = AddContactView.as_view()
        # Создаем активного пользователя
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True)
        # Создаем токен для пользователя
        self.access_token = AccessToken.for_user(self.user)

    def test_add_contact_view(self):
        """Тест на успешное добавление контактных данных"""
        contact_data = {
            'city': 'Москва',
            'street': 'Ленинградская',
            'house': '12',
            'phone': '+79211234567'
        }
        request = self.factory.post('/api/v1/add-contact/', contact_data, format='json')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)