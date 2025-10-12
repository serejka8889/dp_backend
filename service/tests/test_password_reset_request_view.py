from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import PasswordResetRequestView
from service.models import CustomUser

class PasswordResetRequestViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PasswordResetRequestView.as_view()
        # Создаем зарегистрированного пользователя
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True)

    def test_password_reset_request_view(self):
        """Тест на успешный запрос восстановления пароля"""
        reset_data = {'email': 'test@example.com'}
        request = self.factory.post('/api/v1/password/reset/', reset_data, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)