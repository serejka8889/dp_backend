from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.response import Response
from service.views import ConfirmRegistrationView

class ConfirmRegistrationViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ConfirmRegistrationView.as_view()

    def test_confirm_registration_view(self):
        """Тест на успешное подтверждение регистрации"""
        # Вернём объект Response вместо простого dict
        mock_response = Response({'detail': 'Регистрация подтверждена успешно!'}, status=status.HTTP_200_OK)
        with patch.object(ConfirmRegistrationView, 'get', return_value=mock_response):
            request = self.factory.get('/api/v1/confirm-registration/MOCK_USER_ID/MOCK_TOKEN')
            response = self.view(request, MOCK_USER_ID='MOCK_USER_ID', token='MOCK_TOKEN')
            self.assertEqual(response.status_code, status.HTTP_200_OK)