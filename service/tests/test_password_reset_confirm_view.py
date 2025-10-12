from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import ConfirmPasswordResetView
from service.models import CustomUser, PasswordResetToken
from datetime import timedelta
from django.utils.timezone import now

class ConfirmPasswordResetViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ConfirmPasswordResetView.as_view()
        # Создаем зарегистрированного пользователя
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True)
        # Создаем токен сброса пароля для этого пользователя
        expires_at = now() + timedelta(hours=1)
        self.password_reset_token = PasswordResetToken.objects.create(user=self.user, token='VALID_RESET_TOKEN', expires_at=expires_at)

    def test_confirm_password_reset_view(self):
        """Тест на успешное подтверждение восстановления пароля"""
        new_password = 'MyVerySecurePassword123!'
        # Данные для подтверждения сброса пароля
        confirm_data = {
            'token': self.password_reset_token.token,
            'new_password': new_password
        }
        # Отправляем запрос
        request = self.factory.post('/api/v1/password/reset/confirmation/', confirm_data, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Опционально: проверка того, что пароль действительно сменился
        updated_user = CustomUser.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.check_password(new_password))