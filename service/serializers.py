from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import FileField
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .tasks import *


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода данных пользователя.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Сериализатор для отправки запроса на сброс пароля.
    """
    email = serializers.EmailField(label="Email", max_length=254)

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Данный email не зарегистрирован.")
        return value

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    """
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = get_user_model().objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(password)
        user.save()
        send_registration_confirmation_email.delay(user.id)
        return user

class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователя.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Невозможно войти с указанными учетными данными.', code='authorization')
        elif not user.is_active:
            raise serializers.ValidationError('Аккаунт деактивирован.', code='inactive_account')
        return attrs

    def create(self, validated_data):
        user = authenticate(username=validated_data['email'], password=validated_data['password'])
        if user is None:
            raise serializers.ValidationError('Неверные учетные данные.', code='authorization')
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категорий товаров.
    """
    class Meta:
        model = Category
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для товаров.
    Включает вложенную категорию.
    """
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подробной информации о товаре.
    Включает вложенный продукт.
    """
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        exclude = ('external_id', )

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для элементов заказа.
    Включает подробную информацию о продукте.
    """
    product = ProductInfoSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для заказов.
    Включает список позиций заказа и общую сумму.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Order
        fields = ['id', 'items', 'total_amount', 'status', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

class CartItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для товаров в корзине.
    Включает информацию о продукте.
    """
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    model = serializers.CharField(source='product.model', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.price', read_only=True)
    quantity_available = serializers.IntegerField(source='product.quantity', read_only=True)
    shop = serializers.PrimaryKeyRelatedField(source='product.shop', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product_name', 'category_name', 'model', 'price', 'quantity_available', 'shop', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для корзины пользователя.
    Включает товары в корзине.
    """
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items']

class AddToCartItemSerializer(serializers.Serializer):
    """
    Сериализатор для добавления товара в корзину.
    """
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class MultipleCartItemsSerializer(serializers.ListSerializer):
    """
    Сериализатор для множества товаров в корзине.
    """
    child = AddToCartItemSerializer()

class ImportFileSerializer(serializers.Serializer):
    """
    Сериализатор для импорта файлов.
    """
    file = FileField(use_url=True)

class ContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для контактных данных пользователя.
    """
    class Meta:
        model = Contact
        fields = ['city', 'street', 'house', 'phone', 'structure', 'building', 'apartment']

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Сериализатор для отправки запроса на сброс пароля.
    """
    email = serializers.EmailField(label="Email", max_length=254)

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Данный email не зарегистрирован.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля.
    """
    token = serializers.CharField(label="Токен", max_length=64)
    new_password = serializers.CharField(label="Новый пароль", min_length=8, write_only=True)

    def validate(self, data):
        token = data.get('token')
        try:
            token_obj = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Некорректный токен.")
        if token_obj.expires_at <= timezone.now():
            raise serializers.ValidationError("Срок действия токена истек.")
        return data