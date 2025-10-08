from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView
from service.views import HomePageView


schema_view = get_schema_view(
    openapi.Info(
        title="Your Project API Documentation",
        default_version='v1',
        description="Документация API для вашего проекта.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Роуты приложения
    path('api/v1/', include('service.urls')),
    path('', HomePageView.as_view(), name='home'),

    # Роуты для соцсетей
    path('auth/', include('social_django.urls', namespace='social')),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Обновление токенов

    # Документирование API с помощью Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Документирование API с помощью ReDoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
