from django.contrib import admin
from .models import CustomUser, Shop, Product, ProductInfo, Order, OrderItem, Contact, Cart, CartItem

# Класс администрирования для пользователя
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

# Класс администрирования для магазина
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'state')
    list_filter = ('state',)
    search_fields = ('name',)

# Класс администрирования для продукта
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

# Класс администрирования для информации о продукте
@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'model', 'price', 'quantity', 'shop')
    list_filter = ('shop',)
    search_fields = ('product__name', 'model')

# Класс администрирования для заказа
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email',)

# Класс администрирования для элементов заказа
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    list_filter = ('order',)
    search_fields = ('product__name',)

# Класс администрирования для контактов
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'street', 'house', 'phone')
    list_filter = ('city',)
    search_fields = ('user__email', 'city')

# Класс администрирования для корзины
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user_safe', 'id')

    def user_safe(self, obj):
        return obj.user if obj.user else '(Пользователь неизвестен)'
    user_safe.short_description = 'Пользователь'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_safe', 'product', 'quantity')
    list_filter = ('cart',)
    search_fields = ('product__name',)

    def cart_safe(self, obj):
        return obj.cart if obj.cart else '(Без корзины)'
    cart_safe.short_description = 'Корзина'