from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import SetOrderStatusView
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser, Order, Product, ProductInfo, Category, Shop, OrderItem  # Импортируем необходимые модели
from decimal import Decimal

class SetOrderStatusViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = SetOrderStatusView.as_view()
        # Создаем активного пользователя
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True)
        # Создаем токен для пользователя
        self.access_token = AccessToken.for_user(self.user)
        # Создаем категорию
        self.category = Category.objects.create(name='Electronics')
        # Создаем магазин
        self.shop = Shop.objects.create(name='Tech Store')
        # Создаем товар
        self.product = Product.objects.create(name='Smartphone', category=self.category)
        # Создаем подробную информацию о товаре
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            external_id=1,
            model='Model X',
            price=Decimal('999.99'),
            quantity=10,
            shop=self.shop
        )
        # Создаем заказ
        self.order = Order.objects.create(user=self.user, total_amount=Decimal('1999.98'))
        # Добавляем позицию в заказ
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product_info, quantity=2)

    def test_set_order_status_view(self):
        """Тест на успешное изменение статуса заказа"""
        # Данные для изменения статуса заказа
        update_data = {'status': 'confirmed'}  # Соответствует вашему curl-запросу
        # Формируем PATCH-запрос с токеном авторизации
        request = self.factory.patch(f'/api/v1/set-order-status/{self.order.id}/', update_data, format='json')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request, pk=self.order.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что статус заказа изменился
        updated_order = Order.objects.get(pk=self.order.id)
        self.assertEqual(updated_order.status, 'confirmed')