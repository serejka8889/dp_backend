import requests

RESET_PASSWORD_TOKEN = '<your-received-token>'
ACCESS_TOKEN = ''

# 1️ Регистрация нового пользователя
response = requests.post(
    "http://localhost:8000/api/v1/register",
    json={
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "strongpassword123"
    },
)
print(f'POST /api/v1/register — статус-код {response.status_code}')
if response.status_code != 201:
    print('Ошибка регистрации пользователя')
else:
    print(response.json())

# 2️ Логин пользователя
response = requests.post(
    "http://localhost:8000/api/v1/login",
    json={
        "email": "test@example.com",
        "password": "strongpassword123"
    },
)
print(f'POST /api/v1/login — статус-код {response.status_code}')
if response.status_code != 200:
    print('Ошибка авторизации')
else:
    auth_response = response.json()
    print(auth_response)
    ACCESS_TOKEN = auth_response['access']

# 3️ Добавление товара в корзину
response = requests.post(
    "http://localhost:8000/api/v1/add-to-cart",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    json=[
        {"product": 1, "quantity": 2},
        {"product": 4, "quantity": 1}
    ],
)
print(f'POST /api/v1/add-to-cart — статус-код {response.status_code}')
if response.status_code != 201:
    print('Ошибка добавления товара в корзину')
else:
    print(response.json())

# 4️ Просмотр корзины
response = requests.get(
    "http://localhost:8000/api/v1/cart",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
)
print(f'GET /api/v1/cart — статус-код {response.status_code}')
if response.status_code != 200:
    print('Ошибка просмотра корзины')
else:
    print(response.json())

# 5️ Удаление товара из корзины
response = requests.delete(
    "http://localhost:8000/api/v1/remove-from-cart/1",  # Предположим, удаляется первый товар из корзины
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
)
print(f'DELETE /api/v1/remove-from-cart/1 — статус-код {response.status_code}')
if response.status_code != 204:
    print('Ошибка удаления товара из корзины')
else:
    print('Товар успешно удалён из корзины.')

# 6️ Создание заказа
response = requests.post(
    "http://localhost:8000/api/v1/place-order",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    json={
        "contact": {
            "city": "Москва",
            "street": "Ленинградский проспект",
            "house": "35",
            "phone": "+79991234567"
        }
    },
)
print(f'POST /api/v1/place-order — статус-код {response.status_code}')
if response.status_code != 201:
    print('Ошибка создания заказа')
else:
    print(response.json())

# 7️ Получение списка заказов
response = requests.get(
    "http://localhost:8000/api/v1/orders",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
)
print(f'GET /api/v1/orders — статус-код {response.status_code}')
if response.status_code != 200:
    print('Ошибка получения списка заказов')
else:
    print(response.json())

# 8️ Детали конкретного заказа
response = requests.get(
    "http://localhost:8000/api/v1/order/1",  # Предположим, хотим посмотреть заказ с номером 1
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
)
print(f'GET /api/v1/order/1 — статус-код {response.status_code}')
if response.status_code != 200:
    print('Ошибка получения детализированной информации о заказе')
else:
    print(response.json())

# 9 Заказы партнёра
response = requests.get(
    "http://localhost:8000/api/v1/partner-orders",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
)
print(f'GET /api/v1/partner-orders — статус-код {response.status_code}')
if response.status_code != 200:
    print('Ошибка получения заказов партнёра')
else:
    print(response.json())

# 10 Состояние партнерского аккаунта
response = requests.patch(
    "http://localhost:8000/api/v1/partner-state",
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    json={"state": True},  # Активирует аккаунт поставщика
)
print(f'PATCH /api/v1/partner-state — статус-код {response.status_code}')
if response.status_code != 200:
    print('Ошибка изменения состояния партнерского аккаунта')
else:
    print(response.json())

# 11 Импорт товаров
with open('./example_products.csv', 'rb') as file:
    response = requests.post(
        "http://localhost:8000/api/v1/import-products",
        files={"file": file},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
print(f'POST /api/v1/import-products — статус-код {response.status_code}')
if response.status_code != 202:
    print('Ошибка загрузки товаров')
else:
    print(response.json())
