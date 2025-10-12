from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import RegisterView
from service.models import CustomUser

class RegisterViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RegisterView.as_view()

    def test_register_view(self):
        """Тест на успешную регистрацию пользователя"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'StrongPass123',
            'confirm_password': 'StrongPass123'
        }
        request = self.factory.post('/api/v1/register/', register_data, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)