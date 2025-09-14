# urls.py
from django.urls import path
from .views import (
    UsersListView, UserDetailView, UserCreateView, UserUpdateView, UserDeleteView,
    ShopsListView, ShopDetailView, ShopCreateView, ShopUpdateView, ShopDeleteView,
    ProductsListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    ProductInfosListView, ProductInfoDetailView, ProductInfoCreateView, ProductInfoUpdateView, ProductInfoDeleteView,
    OrdersListView, OrderDetailView, OrderCreateView, OrderUpdateView, OrderDeleteView,
    OrderItemsListView, OrderItemDetailView, OrderItemCreateView, OrderItemUpdateView, OrderItemDeleteView,
    ContactsListView, ContactDetailView, ContactCreateView, ContactUpdateView, ContactDeleteView,
    CartsListView, CartDetailView, CartCreateView, CartUpdateView, CartDeleteView,
    CartItemsListView, CartItemDetailView, CartItemCreateView, CartItemUpdateView, CartItemDeleteView
)

urlpatterns = [
    # Пользователи
    path('users/', UsersListView.as_view(), name='users-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/add/', UserCreateView.as_view(), name='user-add'),
    path('users/edit/<int:pk>/', UserUpdateView.as_view(), name='user-edit'),
    path('users/delete/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),

    # Магазины
    path('shops/', ShopsListView.as_view(), name='shops-list'),
    path('shops/<int:pk>/', ShopDetailView.as_view(), name='shop-detail'),
    path('shops/add/', ShopCreateView.as_view(), name='shop-add'),
    path('shops/edit/<int:pk>/', ShopUpdateView.as_view(), name='shop-edit'),
    path('shops/delete/<int:pk>/', ShopDeleteView.as_view(), name='shop-delete'),

    # Продукты
    path('products/', ProductsListView.as_view(), name='products-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/add/', ProductCreateView.as_view(), name='product-add'),
    path('products/edit/<int:pk>/', ProductUpdateView.as_view(), name='product-edit'),
    path('products/delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),

    # Информации о продукте
    path('productinfos/', ProductInfosListView.as_view(), name='productinfos-list'),
    path('productinfos/<int:pk>/', ProductInfoDetailView.as_view(), name='productinfo-detail'),
    path('productinfos/add/', ProductInfoCreateView.as_view(), name='productinfo-add'),
    path('productinfos/edit/<int:pk>/', ProductInfoUpdateView.as_view(), name='productinfo-edit'),
    path('productinfos/delete/<int:pk>/', ProductInfoDeleteView.as_view(), name='productinfo-delete'),

    # Заказы
    path('orders/', OrdersListView.as_view(), name='orders-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/add/', OrderCreateView.as_view(), name='order-add'),
    path('orders/edit/<int:pk>/', OrderUpdateView.as_view(), name='order-edit'),
    path('orders/delete/<int:pk>/', OrderDeleteView.as_view(), name='order-delete'),

    # Элементы заказа
    path('orderitems/', OrderItemsListView.as_view(), name='orderitems-list'),
    path('orderitems/<int:pk>/', OrderItemDetailView.as_view(), name='orderitem-detail'),
    path('orderitems/add/', OrderItemCreateView.as_view(), name='orderitem-add'),
    path('orderitems/edit/<int:pk>/', OrderItemUpdateView.as_view(), name='orderitem-edit'),
    path('orderitems/delete/<int:pk>/', OrderItemDeleteView.as_view(), name='orderitem-delete'),

    # Контакты пользователей
    path('contacts/', ContactsListView.as_view(), name='contacts-list'),
    path('contacts/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
    path('contacts/add/', ContactCreateView.as_view(), name='contact-add'),
    path('contacts/edit/<int:pk>/', ContactUpdateView.as_view(), name='contact-edit'),
    path('contacts/delete/<int:pk>/', ContactDeleteView.as_view(), name='contact-delete'),

    # Корзины
    path('carts/', CartsListView.as_view(), name='carts-list'),
    path('carts/<int:pk>/', CartDetailView.as_view(), name='cart-detail'),
    path('carts/add/', CartCreateView.as_view(), name='cart-add'),
    path('carts/edit/<int:pk>/', CartUpdateView.as_view(), name='cart-edit'),
    path('carts/delete/<int:pk>/', CartDeleteView.as_view(), name='cart-delete'),

    # Элементы корзины
    path('cartitems/', CartItemsListView.as_view(), name='cartitems-list'),
    path('cartitems/<int:pk>/', CartItemDetailView.as_view(), name='cartitem-detail'),
    path('cartitems/add/', CartItemCreateView.as_view(), name='cartitem-add'),
    path('cartitems/edit/<int:pk>/', CartItemUpdateView.as_view(), name='cartitem-edit'),
    path('cartitems/delete/<int:pk>/', CartItemDeleteView.as_view(), name='cartitem-delete'),
]