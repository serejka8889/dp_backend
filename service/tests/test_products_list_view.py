from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from rest_framework.response import Response
from service.views import ProductsListView

class ProductsListViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ProductsListView.as_view()

    def test_products_list_view(self):
        """Тест на успешное получение списка товаров"""
        # Подготовьте тестовые данные продуктов
        product_data = [{'id': 1, 'name': 'Product'}]
        # Возвращаем объект Response с данными продукта
        mock_response = Response(product_data, status=status.HTTP_200_OK)
        with patch.object(ProductsListView, 'get', return_value=mock_response):
            request = self.factory.get('/api/v1/products/')
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), len(product_data))  # Проверка количества элементов