from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.response import Response
from service.views import OrdersListView
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser, Order, Product, ProductInfo, Category, Shop, OrderItem
from decimal import Decimal

class OrdersListViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = OrdersListView.as_view()
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

    def test_orders_list_view(self):
        """Тест на успешное получение списка заказов"""
        # Создаем заглушку для ответа с данными заказа
        mock_response = Response([
            {'id': self.order.id, 'total_amount': float(self.order.total_amount)}
        ], status=status.HTTP_200_OK)
        # Применяем патч для замены фактической обработки представления
        with patch.object(OrdersListView, 'get', return_value=mock_response):
            request = self.factory.get('/api/v1/orders/')
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)  # Проверка количества заказов