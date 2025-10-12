from django.urls import path
from .views import *

urlpatterns = [
    # Пользователи
    path('login/', LoginView.as_view(), name='login'),              # Вход пользователя
    path('register/', RegisterView.as_view(), name='register'),    # Регистрация пользователя
    path('confirm-registration/<int:user_id>/<path:token>/', ConfirmRegistrationView.as_view(), name='confirm-registration'),   # Восстановление пароля
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),   # Подтверждения восстановления пароля
    path('password/reset/confirmation/', ConfirmPasswordResetView.as_view(), name='password_reset_confirm'),   # Подтверждения регистрации пользователя

    # Товары и инвентарь
    path('products/', ProductsListView.as_view(), name='products-list'),           # Список товаров
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),            # Добавление товара в корзину
    path('remove-from-cart/<int:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),  # Удаление товара из корзины
    path('cart/', CartView.as_view(), name='cart-detail'),                         # Просмотр корзины

    # Заказы
    path('orders/', OrdersListView.as_view(), name='orders-list'),                 # Список заказов
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),       # Детали конкретного заказа
    path('place-order/', PlaceOrderView.as_view(), name='place-order'),            # Оформление заказа
    path('set-order-status/<int:pk>/', SetOrderStatusView.as_view(), name='set-order-status'),       # Изменение состояния заказа

    # Партнеры
    path('partner-state/', PartnerState.as_view(), name='partner-state'),          # Состояние магазина партнера
    path('partner-update/', PartnerUpdate.as_view(), name='partner-update'),       # Обновление прайса партнером

    # Импорт и экспорт данных
    path('import-products/', ImportProductsView.as_view(), name='import-products'),  # Импорт товаров из файла
    path('export-products/', ExportProductsView.as_view(), name='export-products'),  # Экспорт товаров в файл

    # Контакты
    path('add-contact/', AddContactView.as_view(), name='add-contact'),             # Добавление контактных данных
    path('delete-contact/<int:pk>/', DeleteContactView.as_view(), name='delete_contact'),    # Удаление контактных данных

    path('trigger-test/', TriggerTestException.as_view(), name='trigger_test'),  # Роут для проверки ошибки в Rollbar
]
