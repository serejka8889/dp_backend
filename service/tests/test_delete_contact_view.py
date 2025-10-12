from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import DeleteContactView
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser, Contact

class DeleteContactViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = DeleteContactView.as_view()
        # Создаем активного пользователя
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True)
        # Создаем токен для пользователя
        self.access_token = AccessToken.for_user(self.user)
        # Создаем контактные данные для удаления
        self.contact = Contact.objects.create(user=self.user, city='Москва', street='ул. Ленина', house='12')

    def test_delete_contact_view(self):
        """Тест на успешное удаление контактных данных"""
        # Формируем DELETE-запрос с токеном авторизации
        request = self.factory.delete(f'/api/v1/delete-contact/{self.contact.id}/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request, pk=self.contact.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Проверяем, что контакт удалён
        with self.assertRaises(Contact.DoesNotExist):
            Contact.objects.get(pk=self.contact.id)