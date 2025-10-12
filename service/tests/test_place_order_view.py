from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import PlaceOrderView
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser, Product, ProductInfo, Category, Shop, Cart, CartItem, Order
from decimal import Decimal

class PlaceOrderViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PlaceOrderView.as_view()
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
        # Получаем или создаем корзину пользователя
        self.cart, _ = Cart.objects.get_or_create(user=self.user)
        # Добавляем позицию в корзину
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product_info, quantity=2)

    def test_place_order_view(self):
        """Тест на успешное оформление заказа"""
        # Формируем POST-запрос с токеном авторизации
        request = self.factory.post('/api/v1/place-order/', {}, format='json')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Проверяем, что заказ создан
        self.assertGreater(Order.objects.count(), 0)