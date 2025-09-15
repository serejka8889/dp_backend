# forms.py
from django import forms
from service.models import CustomUser, Shop, Product, ProductInfo, Order, OrderItem, Contact, Cart, CartItem

class CustomUserForm(forms.ModelForm):
    """Форма для пользователя."""
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'role', 'is_active']

class ShopForm(forms.ModelForm):
    """Форма для магазина."""
    class Meta:
        model = Shop
        fields = ['name', 'user', 'state']

class ProductForm(forms.ModelForm):
    """Форма для продукта."""
    class Meta:
        model = Product
        fields = ['name', 'category']

class ProductInfoForm(forms.ModelForm):
    """Форма для подробной информации о продукте."""
    class Meta:
        model = ProductInfo
        fields = ['product', 'external_id', 'model', 'price', 'quantity', 'shop']

class OrderForm(forms.ModelForm):
    """Форма для заказа."""
    class Meta:
        model = Order
        fields = ['user', 'total_amount', 'status']

class OrderItemForm(forms.ModelForm):
    """Форма для элемента заказа."""
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity']

class ContactForm(forms.ModelForm):
    """Форма для контактных данных пользователя."""
    class Meta:
        model = Contact
        fields = ['user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone']

class CartForm(forms.ModelForm):
    """Форма для корзины пользователя."""
    class Meta:
        model = Cart
        fields = ['user']

class CartItemForm(forms.ModelForm):
    """Форма для элемента корзины."""
    class Meta:
        model = CartItem
        fields = ['cart', 'product', 'quantity']
