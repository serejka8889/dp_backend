from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import status
from service.views import LoginView
from service.models import CustomUser

class LoginViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = LoginView.as_view()
        # Создаем активного пользователя
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True)

    def test_login_view(self):
        """Тест на успешный логин пользователя"""
        # Данные для входа
        login_data = {'email': 'test@example.com', 'password': 'password'}
        request = self.factory.post('/api/v1/login/', login_data, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)