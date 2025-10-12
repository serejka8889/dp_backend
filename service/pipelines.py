import json
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse

logger = logging.getLogger(__name__)

def jwt_response_with_refresh_token(strategy, details, backend, request=None, *args, **kwargs):
    user = kwargs['user']
    refresh = RefreshToken.for_user(user)  # Генерация JWT-токена
    response_data = {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
    }

    # Выводим токены и данные пользователя в консоль
    # logger.info(f"Access Token (токен доступа): {response_data['access']}")
    # logger.info(f"Refresh Token (обновляющий токен): {response_data['refresh']}")
    # logger.info(f"Данные пользователя:\nID пользователя: {response_data['user_id']}\nЭлектронная почта: {response_data['email']}\nРоль: {response_data['role']} ({response_data['role'].capitalize()})")

    return HttpResponse(json.dumps(response_data), content_type='application/json')
