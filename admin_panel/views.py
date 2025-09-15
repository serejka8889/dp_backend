# views.py
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import CustomUserForm, ShopForm, ProductForm, ProductInfoForm, OrderForm, OrderItemForm, ContactForm, CartForm, CartItemForm
from service.models import CustomUser, Shop, Product, ProductInfo, Order, OrderItem, Contact, Cart, CartItem

# Пользователи
class UsersListView(ListView):
    """Просмотр списка пользователей"""
    model = CustomUser
    template_name = 'users_list.html'
    context_object_name = 'users'

class UserDetailView(DetailView):
    """Детальная страница пользователя"""
    model = CustomUser
    template_name = 'user_detail.html'
    context_object_name = 'user'

class UserCreateView(CreateView):
    """Создание нового пользователя"""
    form_class = CustomUserForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('users-list')

class UserUpdateView(UpdateView):
    """Обновление профиля пользователя"""
    model = CustomUser
    form_class = CustomUserForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('users-list')

class UserDeleteView(DeleteView):
    """Удаление пользователя"""
    model = CustomUser
    success_url = reverse_lazy('users-list')
    template_name = 'user_confirm_delete.html'

# Магазины
class ShopsListView(ListView):
    """Просмотр списка магазинов"""
    model = Shop
    template_name = 'shops_list.html'
    context_object_name = 'shops'

class ShopDetailView(DetailView):
    """Детальная страница магазина"""
    model = Shop
    template_name = 'shop_detail.html'
    context_object_name = 'shop'

class ShopCreateView(CreateView):
    """Создание нового магазина"""
    form_class = ShopForm
    template_name = 'shop_form.html'
    success_url = reverse_lazy('shops-list')

class ShopUpdateView(UpdateView):
    """Обновление магазина"""
    model = Shop
    form_class = ShopForm
    template_name = 'shop_form.html'
    success_url = reverse_lazy('shops-list')

class ShopDeleteView(DeleteView):
    """Удаление магазина"""
    model = Shop
    success_url = reverse_lazy('shops-list')
    template_name = 'shop_confirm_delete.html'

# Продукты
class ProductsListView(ListView):
    """Просмотр списка продуктов"""
    model = Product
    template_name = 'products_list.html'
    context_object_name = 'products'

class ProductDetailView(DetailView):
    """Детальная страница продукта"""
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

class ProductCreateView(CreateView):
    """Создание нового продукта"""
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('products-list')

class ProductUpdateView(UpdateView):
    """Обновление продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('products-list')

class ProductDeleteView(DeleteView):
    """Удаление продукта"""
    model = Product
    success_url = reverse_lazy('products-list')
    template_name = 'product_confirm_delete.html'

# Информационная карточка продукта
class ProductInfosListView(ListView):
    """Просмотр списка информационной карточки продукта"""
    model = ProductInfo
    template_name = 'productinfos_list.html'
    context_object_name = 'productinfos'

class ProductInfoDetailView(DetailView):
    """Детальная страница информационной карточки продукта"""
    model = ProductInfo
    template_name = 'productinfo_detail.html'
    context_object_name = 'productinfo'

class ProductInfoCreateView(CreateView):
    """Создание новой информационной карточки продукта"""
    form_class = ProductInfoForm
    template_name = 'productinfo_form.html'
    success_url = reverse_lazy('productinfos-list')

class ProductInfoUpdateView(UpdateView):
    """Обновление информационной карточки продукта"""
    model = ProductInfo
    form_class = ProductInfoForm
    template_name = 'productinfo_form.html'
    success_url = reverse_lazy('productinfos-list')

class ProductInfoDeleteView(DeleteView):
    """Удаление информационной карточки продукта"""
    model = ProductInfo
    success_url = reverse_lazy('productinfos-list')
    template_name = 'productinfo_confirm_delete.html'

# Заказы
class OrdersListView(ListView):
    """Просмотр списка заказов"""
    model = Order
    template_name = 'orders_list.html'
    context_object_name = 'orders'

class OrderDetailView(DetailView):
    """Детальная страница заказа"""
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

class OrderCreateView(CreateView):
    """Создание нового заказа"""
    form_class = OrderForm
    template_name = 'order_form.html'
    success_url = reverse_lazy('orders-list')

class OrderUpdateView(UpdateView):
    """Обновление заказа"""
    model = Order
    form_class = OrderForm
    template_name = 'order_form.html'
    success_url = reverse_lazy('orders-list')

class OrderDeleteView(DeleteView):
    """Удаление заказа"""
    model = Order
    success_url = reverse_lazy('orders-list')
    template_name = 'order_confirm_delete.html'

# Элементы заказа
class OrderItemsListView(ListView):
    """Просмотр списка элементов заказа"""
    model = OrderItem
    template_name = 'orderitems_list.html'
    context_object_name = 'orderitems'

class OrderItemDetailView(DetailView):
    """Детальная страница элемента заказа"""
    model = OrderItem
    template_name = 'orderitem_detail.html'
    context_object_name = 'orderitem'

class OrderItemCreateView(CreateView):
    """Создание нового элемента заказа"""
    form_class = OrderItemForm
    template_name = 'orderitem_form.html'
    success_url = reverse_lazy('orderitems-list')

class OrderItemUpdateView(UpdateView):
    """Обновление элемента заказа"""
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orderitem_form.html'
    success_url = reverse_lazy('orderitems-list')

class OrderItemDeleteView(DeleteView):
    """Удаление элемента заказа"""
    model = OrderItem
    success_url = reverse_lazy('orderitems-list')
    template_name = 'orderitem_confirm_delete.html'

# Контакты пользователей
class ContactsListView(ListView):
    """Просмотр списка контактов пользователей"""
    model = Contact
    template_name = 'contacts_list.html'
    context_object_name = 'contacts'

class ContactDetailView(DetailView):
    """Детальная страница контакта пользователя"""
    model = Contact
    template_name = 'contact_detail.html'
    context_object_name = 'contact'

class ContactCreateView(CreateView):
    """Создание нового контакта пользователя"""
    form_class = ContactForm
    template_name = 'contact_form.html'
    success_url = reverse_lazy('contacts-list')

class ContactUpdateView(UpdateView):
    """Обновление контакта пользователя"""
    model = Contact
    form_class = ContactForm
    template_name = 'contact_form.html'
    success_url = reverse_lazy('contacts-list')

class ContactDeleteView(DeleteView):
    """Удаление контакта пользователя"""
    model = Contact
    success_url = reverse_lazy('contacts-list')
    template_name = 'contact_confirm_delete.html'

# Корзины
class CartsListView(ListView):
    """Просмотр списка корзин пользователей"""
    model = Cart
    template_name = 'carts_list.html'
    context_object_name = 'carts'

class CartDetailView(DetailView):
    """Детальная страница корзины пользователя"""
    model = Cart
    template_name = 'cart_detail.html'
    context_object_name = 'cart'

class CartCreateView(CreateView):
    """Создание новой корзины пользователя"""
    form_class = CartForm
    template_name = 'cart_form.html'
    success_url = reverse_lazy('carts-list')

class CartUpdateView(UpdateView):
    """Обновление корзины пользователя"""
    model = Cart
    form_class = CartForm
    template_name = 'cart_form.html'
    success_url = reverse_lazy('carts-list')

class CartDeleteView(DeleteView):
    """Удаление корзины пользователя"""
    model = Cart
    success_url = reverse_lazy('carts-list')
    template_name = 'cart_confirm_delete.html'

# Элементы корзины
class CartItemsListView(ListView):
    """Просмотр списка элементов корзины"""
    model = CartItem
    template_name = 'cartitems_list.html'
    context_object_name = 'cartitems'

class CartItemDetailView(DetailView):
    """Детальная страница элемента корзины"""
    model = CartItem
    template_name = 'cartitem_detail.html'
    context_object_name = 'cartitem'

class CartItemCreateView(CreateView):
    """Создание нового элемента корзины"""
    form_class = CartItemForm
    template_name = 'cartitem_form.html'
    success_url = reverse_lazy('cartitems-list')

class CartItemUpdateView(UpdateView):
    """Обновление элемента корзины"""
    model = CartItem
    form_class = CartItemForm
    template_name = 'cartitem_form.html'
    success_url = reverse_lazy('cartitems-list')

class CartItemDeleteView(DeleteView):
    """Удаление элемента корзины"""
    model = CartItem
    success_url = reverse_lazy('cartitems-list')
    template_name = 'cartitem_confirm_delete.html'
