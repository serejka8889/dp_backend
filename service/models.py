import base64
from datetime import timedelta
import jwt
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, AbstractUser
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.core.validators import MinValueValidator
from service.managers import CustomUserManager
from versatileimagefield.fields import VersatileImageField, PPOIField


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Расширенная модель пользователя с дополнительной ролью.
    Наследуется от AbstractBaseUser, что даёт стандартную функциональность пользователя.
    """
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),  # Покупатель
        ('seller', 'Seller'),  # Поставщик
    ]
    email = models.EmailField(unique=True, verbose_name='Email')  # Почта пользователя становится уникальным полем
    first_name = models.CharField(max_length=30, verbose_name='First Name')  # Имя
    last_name = models.CharField(max_length=30, verbose_name='Last Name')  # Фамилия
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')  # Роль пользователя
    is_active = models.BooleanField(default=True, verbose_name='Active')  # Активность аккаунта
    is_staff = models.BooleanField(default=False, verbose_name='Staff Status')  # Необходимое поле для администратора
    is_superuser = models.BooleanField(default=False, verbose_name='Superuser Status')  # Необходимо для суперпользователя
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Date joined')  # Дата регистрации
    avatar = VersatileImageField('Avatar', upload_to='avatars/',  ppoi_field='avatar_ppoi', blank=True, null=True)
    avatar_ppoi = PPOIField()

    USERNAME_FIELD = 'email'  # Основное поле идентификации - почта
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    # Определим уникальные имена для reverse-accessor
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="customuser_groups",
        related_query_name="customuser_group",
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions",  # Уникальный related_name для разрешений
        related_query_name="customuser_permission",
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('email',)

    def generate_confirmation_token(self):
        """Генерация временного токена для подтверждения регистрации."""
        payload = {
            'user_id': self.id,
            'exp': timezone.now() + timezone.timedelta(hours=24)  # Токен действует сутки
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return token

class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(length=64)
        if not self.expires_at:
            self.expires_at = now() + timedelta(hours=24)
        super().save(*args, **kwargs)


class Category(models.Model):
    """
    Модель категорий товаров.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Название категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Shop(models.Model):
    """
    Магазин-поставщик.
    """
    name = models.CharField(max_length=80, unique=True, verbose_name='Название магазина')  # Название магазина
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="shop", null=True, blank=True, verbose_name='Связанный пользователь')  # Связанный пользователь
    state = models.BooleanField(verbose_name='Активность', default=True)  # Текущее состояние активности магазина

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Основной товар.
    """
    name = models.CharField(max_length=150, verbose_name='Название продукта')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name='Категория')  # К какой категории относится товар
    image = VersatileImageField('Product Image', upload_to='products/', ppoi_field='image_ppoi', blank=True, null=True)
    image_ppoi = PPOIField()

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name

class ProductInfo(models.Model):
    """
    Подробная информация о товаре.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="infos", verbose_name='Продукт')  # Товар
    external_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='Внешний ID')  # Внешний идентификатор
    model = models.CharField(max_length=80, verbose_name='Модель')  # Модель товара
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Цена')  # Цена товара
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], verbose_name='Количество')  # Количество товара
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="product_infos", verbose_name='Магазин')  # Магазин-продавец

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информационные карточки продуктов'

    def __str__(self):
        return f'{self.product}: {self.shop}'

class Order(models.Model):
    """
    Заказ покупателя.
    """
    STATUS_CHOICES = [
        ("new", "Новый"),  # Новый заказ
        ("confirmed", "Подтвержден"),  # Подтвержденный заказ
        ("assembled", "Собран"),  # Собранный заказ
        ("sent", "Отправлен"),  # Отправленный заказ
        ("delivered", "Доставлен"),  # Доставленный заказ
        ("canceled", "Отменен"),  # Отмененный заказ
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders", verbose_name='Заказчик')  # Покупатель
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая сумма')  # Общая сумма заказа
    contact = models.ForeignKey('Contact', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Контакт')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="new", verbose_name='Статус')  # Текущий статус заказа
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')  # Дата создания заказа

    class Meta:
        verbose_name = 'Заказы'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ №{self.pk}'

class OrderItem(models.Model):
    """
    Позиция заказа.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name='Заказ')  # Связанный заказ
    product = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, verbose_name='Продукт')  # Товары в заказе
    quantity = models.PositiveIntegerField(verbose_name='Количество')  # Количество товаров

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'

    def __str__(self):
        return f'{self.order}: {self.product}'

#    def get_total(self):
#        """Возвращает полную цену позиции"""
#        return self.product.price * self.quantity

class Contact(models.Model):
    """
    Контактные данные пользователя.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="contacts", verbose_name='Пользователь')  # Пользователь
    city = models.CharField(max_length=50, verbose_name='Город')  # Город проживания
    street = models.CharField(max_length=100, verbose_name='Улица')  # Улица проживания
    house = models.CharField(max_length=15, verbose_name='Дом')  # Дом проживания
    structure = models.CharField(max_length=15, blank=True, verbose_name='Строение')  # Строение (если применимо)
    building = models.CharField(max_length=15, blank=True, verbose_name='Корпус')  # Корпус (если применимо)
    apartment = models.CharField(max_length=15, blank=True, verbose_name='Квартира')  # Номер квартиры (если применимо)
    phone = models.CharField(max_length=20, verbose_name='Телефон')  # Телефон пользователя

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты пользователей'

    def __str__(self):
        return f'{self.city}, ул.{self.street}, д.{self.house}'

class Cart(models.Model):
    """
    Корзина пользователя.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="cart", verbose_name='Пользователь')  # Пользователь, владеющий корзиной

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    # Создаем корзину автоматически при первом обращении
    @classmethod
    def get_cart(cls, user):
        cart, created = cls.objects.get_or_create(user=user)
        return cart

    def __str__(self):
        return f"Корзина пользователя {self.user.email}"

class CartItem(models.Model):
    """
    Элемент корзины (товар в корзине).
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name='Корзина')  # Корзина, куда добавляется элемент
    product = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, verbose_name='Продукт')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзинах'

    def __str__(self):
        return f"{self.product} ({self.quantity})"