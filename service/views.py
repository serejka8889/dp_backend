import json
from distutils.util import strtobool
from tempfile import NamedTemporaryFile

import jwt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView, \
    GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .tasks import async_import_products, async_send_order_confirmation, send_password_reset_email, \
    send_admin_invoice_email, async_export_products
from .models import Shop, Order, CustomUser, Product, ProductInfo, OrderItem, Cart, CartItem, PasswordResetToken, \
    Contact
from .serializers import OrderSerializer, ProductSerializer, CartSerializer, ContactSerializer,  \
    RegistrationSerializer, LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, \
    MultipleCartItemsSerializer

import logging

logger = logging.getLogger(__name__)

# Авторизация пользователя
class LoginView(CreateAPIView):
    """
    Обработчик POST-запроса на вход пользователя.
    Возвращает JWT-токены для дальнейшего взаимодействия с API.
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        return Response(tokens, status=status.HTTP_200_OK)


# Регистрация пользователя
class RegisterView(CreateAPIView):
    """
    Вид для регистрации новых пользователей.
    """
    serializer_class = RegistrationSerializer


# Список товаров
class ProductsListView(ListAPIView):
    """
    Вид для просмотра списка товаров.
    Поддерживаются фильтры, поиск и сортировка.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'category__name']
    ordering_fields = ['price', 'created_at']


# Просмотр корзины
class CartView(RetrieveAPIView):
    """
    Вид для отображения корзины текущего пользователя.
    Доступно только зарегистрированным пользователям.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        return Cart.get_cart(self.request.user)


# Добавление товара в корзину
class AddToCartView(CreateAPIView):
    """
    Вид для добавления товара в корзину.
    Осуществляет проверку доступности товара на складе.
    """
    serializer_class = MultipleCartItemsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        data = serializer.validated_data
        for item_data in data:
            product_id = item_data.get('product')
            quantity = item_data.get('quantity')
            try:
                product = ProductInfo.objects.get(id=product_id)
            except ProductInfo.DoesNotExist:
                raise serializers.ValidationError(f"Товар с ID {product_id} не найден.")
            if product.quantity < quantity:
                raise serializers.ValidationError(f"Недостаточно товара с ID {product_id} на складе.")
            cart = Cart.get_cart(self.request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
        return Response(status=status.HTTP_201_CREATED)


# Удаление товара из корзины
class RemoveFromCartView(DestroyAPIView):
    """
    Вид для удаления товара из корзины.
    Доступно только владельцу корзины.
    """
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(cart__user=self.request.user)


# Добавление контакта
class AddContactView(CreateAPIView):
    """
    Вид для добавления контактных данных пользователя.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Удаление контакта
class DeleteContactView(DestroyAPIView):
    """
    Вид для удаления контактных данных пользователя.
    """
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


# Подтверждение заказа
class PlaceOrderView(CreateAPIView):
    """
    Вид для подтверждения заказа.
    Автоматически создает заказ из содержимого корзины.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cart = Cart.get_cart(self.request.user)
        total_amount = sum(item.product.price * item.quantity for item in cart.items.all())
        order_items = []
        for cart_item in cart.items.all():
            order_items.append(OrderItem(product=cart_item.product, quantity=cart_item.quantity))
        contact_data = self.request.data.get('contact', {})
        contact = Contact.objects.create(user=self.request.user, **contact_data)
        order = Order.objects.create(user=self.request.user, total_amount=total_amount, contact=contact)
        for item in order_items:
            item.order = order
            item.save()
        cart.items.all().delete()
        send_admin_invoice_email.delay(order.id)
        async_send_order_confirmation.delay(order.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Получение списка заказов
class OrdersListView(ListAPIView):
    """
    Вид для отображения списка заказов пользователя.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# Детали конкретного заказа
class OrderDetailView(RetrieveAPIView):
    """
    Вид для отображения деталей конкретного заказа.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# Импорт товаров
class ImportProductsView(CreateAPIView):
    """
    Вид для загрузки файла с информацией о товарах.
    """
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        file_obj = request.FILES.get("file")
        if file_obj:
            raw_file_data = file_obj.read()
            result = async_import_products.delay(raw_file_data, request.user.id)
            return Response({'task_id': result.task_id}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'detail': 'Нет файла для импорта'}, status=status.HTTP_400_BAD_REQUEST)


class ExportProductsView(CreateAPIView):
    """
    Вид для запуска асинхронного экспорта товаров (только в формате YAML)
    """
    def create(self, request):
        task_result = async_export_products.delay()
        return Response({'task_id': task_result.task_id}, status=status.HTTP_202_ACCEPTED)


# Изменение статуса заказа
class SetOrderStatusView(UpdateAPIView):
    """
    Вид для изменения статуса заказа.
    Отправляет уведомление покупателю после изменений.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        order = serializer.instance
        async_send_order_confirmation.delay(order.id)


# Управление активностью магазина
class PartnerState(UpdateAPIView):
    """
    Вид для изменения активности магазина.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        if request.user.role != 'seller':
            return Response({'Status': False, 'Error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

        try:
            shop = Shop.objects.get(user=request.user)
        except Shop.DoesNotExist:
            return Response({'Status': False, 'Error': 'Магазин не найден'}, status=status.HTTP_404_NOT_FOUND)

        state_data = request.data.get('state')
        if state_data is None:
            return Response({'Status': False, 'Error': 'Параметр state обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        # Удаляем преобразование через json.loads и lower()
        new_state = state_data

        shop.state = new_state
        shop.save()
        return Response({'Status': True}, status=status.HTTP_200_OK)


# Обновление прайса поставщиком
class PartnerUpdate(CreateAPIView):
    """
    Вид для загрузки файла с новыми ценами.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.role != 'seller':
            return Response({'Status': False, 'Error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)
        file = request.FILES.get('file')
        if not file:
            return Response({'Status': False, 'Error': 'Файл не передан'}, status=status.HTTP_400_BAD_REQUEST)
        task = async_import_products.delay(file.read(), request.user.id)
        return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)


# Dосстановление пароля
class PasswordResetRequestView(CreateAPIView):
    """
    Вид для отправки запроса на восстановление пароля.
    """
    serializer_class = PasswordResetRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = CustomUser.objects.get(email=email)
        token = PasswordResetToken.objects.create(user=user)
        send_password_reset_email.delay(user.id, token.token)
        return Response({
            "message": f"Вам отправлено письмо с инструкциями по восстановлению пароля",
        }, status=status.HTTP_200_OK)


# Подтверждения восстановления пароля
class ConfirmPasswordResetView(GenericAPIView):
    """
    Вид для подтверждения восстановления пароля
    """
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        token = validated_data['token']
        new_password = validated_data['new_password']
        token_obj = PasswordResetToken.objects.get(token=token)
        user = token_obj.user
        user.set_password(new_password)
        user.save()
        token_obj.delete()
        return Response({"message": "Пароль успешно восстановлен."}, status=status.HTTP_200_OK)


# Подтверждения регистрации пользователя

User = get_user_model()

class ConfirmRegistrationView(GenericAPIView):
    """
    Вид для подтверждения регистрации пользователя
    """
    authentication_classes = []
    permission_classes = []

    @method_decorator(csrf_exempt)
    def get(self, request, user_id, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload["user_id"] != int(user_id):
                return Response({"detail": "Ошибка токена или несоответствие пользователя"}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({"detail": "Регистрация подтверждена успешно!"}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Время действия токена истекло"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError:
            return Response({"detail": "Невалидный токен"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не существует"}, status=status.HTTP_404_NOT_FOUND)