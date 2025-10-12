from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from service.views import AddToCartView
from rest_framework_simplejwt.tokens import AccessToken
from service.models import CustomUser, Product, ProductInfo, Category, Shop  # Импортируем модели Product, ProductInfo, Category, Shop
from decimal import Decimal

class AddToCartViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = AddToCartView.as_view()
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

    def test_add_to_cart_view(self):
        """Тест на успешное добавление двух товаров в корзину"""
        # Данные для добавления товаров в корзину
        cart_items_data = [
            {'product': self.product_info1.id, 'quantity': 2},
            {'product': self.product_info2.id, 'quantity': 1},
        ]
        # Формируем запрос с токеном авторизации
        request = self.factory.post('/api/v1/add-to-cart/', cart_items_data, format='json')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)