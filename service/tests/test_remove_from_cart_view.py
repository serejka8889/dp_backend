from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import RemoveFromCartView
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser, Product, ProductInfo, Category, Shop, Cart, CartItem  # Импортируем модель Cart и CartItem
from decimal import Decimal

class RemoveFromCartViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RemoveFromCartView.as_view()
        # Создаем активного пользователя
        self.user = CustomUser.objects.create_user(email='test@example.com', password='password', is_active=True)
        # Создаем токен для пользователя
        self.access_token = AccessToken.for_user(self.user)
        # Создаем категорию
        self.category = Category.objects.create(name='Electronics')
        # Создаем магазин
        self.shop = Shop.objects.create(name='Tech Store')
        # Создаем первый товар
        self.product1 = Product.objects.create(name='Smartphone', category=self.category)
        # Создаем подробную информацию о первом товаре
        self.product_info1 = ProductInfo.objects.create(
            product=self.product1,
            external_id=1,
            model='Model X',
            price=Decimal('999.99'),
            quantity=10,
            shop=self.shop
        )
        # Создаем второй товар
        self.product2 = Product.objects.create(name='Headphones', category=self.category)
        # Создаем подробную информацию о втором товаре
        self.product_info2 = ProductInfo.objects.create(
            product=self.product2,
            external_id=2,
            model='Audio Pro',
            price=Decimal('199.99'),
            quantity=5,
            shop=self.shop
        )
        # Получаем или создаем корзину пользователя (получается уникальная корзина)
        self.cart, _ = Cart.objects.get_or_create(user=self.user)
        # Добавляем первую позицию товара в корзину
        self.cart_item1 = CartItem.objects.create(cart=self.cart, product=self.product_info1, quantity=2)
        # Добавляем вторую позицию товара в корзину
        self.cart_item2 = CartItem.objects.create(cart=self.cart, product=self.product_info2, quantity=1)

    def test_remove_from_cart_view(self):
        """Тест на успешное удаление товара из корзины"""
        # Данные для удаления первой позиции товара из корзины
        # Мы удаляем смартфоны (первую позицию)
        request = self.factory.delete(f'/api/v1/remove-from-cart/{self.cart_item1.id}/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request, pk=self.cart_item1.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)