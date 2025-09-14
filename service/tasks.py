import datetime
import os
import time
import traceback
import ssl
from smtplib import SMTPException

import yaml
from celery import shared_task
from django.contrib.auth import models
from django.contrib.auth.models import User
from django.contrib.sites import requests
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.core.mail.backends.smtp import EmailBackend
from django.utils.http import urlsafe_base64_encode
import pandas as pd
from .models import Product, ProductInfo, Shop, Category, Order, CustomUser
import logging

logger = logging.getLogger(__name__)

@shared_task(name="async_send_order_confirmation")
def async_send_order_confirmation(order_id):
    """
    Задача отправляет подтверждение заказа клиенту.
    """
    try:
        order = Order.objects.select_related('user').prefetch_related('items').get(pk=order_id)
        if not order.user.email:
            logger.error(f"Email не указан для пользователя {order.user.email}. Невозможно отправить письмо.")
            return

        items_data = []
        for item in order.items.all():
            product_info = item.product
            items_data.append({
                'product_name': product_info.product.name,
                'model': product_info.model,
                'price': product_info.price,
                'quantity': item.quantity,
                'total_cost': float(product_info.price) * int(item.quantity),
            })

        context = {
            'order': order,
            'items': items_data,
        }

        html_message = render_to_string('emails/order_confirmation.html', context)
        subject = f"Подтверждение заказа №{order.id}"

        result = send_mail(
            subject=subject,
            message='',  # Только HTML-формат письма
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False
        )

        if result > 0:
            logger.info(f"Письмо успешно отправлено покупателю {order.user.email}")
        else:
            logger.warning(f"Ошибка отправки письма покупателю {order.user.email}: результат отправки равен {result}")

    except Order.DoesNotExist:
        logger.error(f"Заказ с номером {order_id} не найден!")
    except Exception as exc:
        logger.exception(f"Ошибка при отправке письма подтверждения: {exc}")


@shared_task(name="async_import_products")
def async_import_products(file_data, user_id):
    """
    Задача импортирует товары из YAML-файла.
    """
    try:
        if isinstance(file_data, bytes):
            file_data = file_data.decode('utf-8')

        data = yaml.safe_load(file_data)

        if 'goods' not in data:
            logger.error("YAML-файл имеет неверную структуру")
            return {'result': 'INVALID_YAML_STRUCTURE'}

        shops_map = {}
        categories_map = {}

        existing_shops = {shop.name: shop for shop in Shop.objects.all()}
        existing_categories = {cat.name: cat for cat in Category.objects.all()}

        for item in data['goods']:
            shop_name = item.get('shop', '')
            if shop_name not in shops_map:
                shop = existing_shops.get(shop_name)
                if not shop:
                    shop = Shop.objects.create(name=shop_name)
                shops_map[shop_name] = shop

            category_name = item.get('category', '')
            if category_name not in categories_map:
                category = existing_categories.get(category_name)
                if not category:
                    category = Category.objects.create(name=category_name)
                categories_map[category_name] = category

            product = Product.objects.get_or_create(name=item['name'], category=categories_map[category_name])

            ProductInfo.objects.update_or_create(
                product=product,
                defaults={
                    'model': item.get('model', ''),
                    'price': float(item.get('price', 0)),
                    'quantity': int(item.get('quantity', 0)),
                    'shop': shops_map[shop_name],
                },
            )

        return {'result': 'IMPORT_SUCCESSFUL'}
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла: {e}")
        return {'result': f'LOADING_ERROR: {str(e)}'}


@shared_task(name="async_export_products")
def async_export_products():
    """
    Задача экспортирует товары в YAML.
    """
    products = ProductInfo.objects.values(
        'product__name', 'model', 'price', 'quantity', 'shop__name', 'product__category__name'
    )

    goods = []
    for product in products:
        goods.append({
            'name': product['product__name'],
            'model': product['model'],
            'price': product['price'],
            'quantity': product['quantity'],
            'shop': product['shop__name'],
            'category': product['product__category__name']
        })

    export_data = {
        'shops': [],
        'categories': [],
        'goods': goods
    }

    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"export{current_time}.yaml"

    with open(os.path.join(settings.EXPORT_DIR, filename), 'w') as outfile:
        yaml.dump(export_data, outfile, allow_unicode=True)

    return {"result": "EXPORT_SUCCESSFUL", "filename": filename}


@shared_task(name="send_password_reset_email")
def send_password_reset_email(user_id, token):
    """
    Задача отправляет письмо с ссылкой для сброса пароля.
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.SITE_URL}/api/v1/password/reset/confirmation/?token={token}&uidb64={uidb64}"

        subject = f"Запрос на восстановление пароля"
        message = render_to_string('emails/password_reset_email.html', {
            'reset_link': reset_link,
            'user': user
        })
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
    except CustomUser.DoesNotExist:
        pass


@shared_task(name="send_admin_invoice_email")
def send_admin_invoice_email(order_id):
    """
    Задача отправляет накладную на заказ администратору магазина.
    """
    try:
        order = Order.objects.prefetch_related('items__product').get(pk=order_id)
        admin_email = settings.ADMIN_EMAIL

        items_data = []
        for item in order.items.all():
            product_info = item.product
            items_data.append({
                'product_name': product_info.product.name,
                'model': product_info.model,
                'price': product_info.price,
                'quantity': item.quantity,
                'total_cost': float(product_info.price) * int(item.quantity),
            })

        context = {
            'order': order,
            'items': items_data,
        }

        html_message = render_to_string('emails/admin_invoice.html', context)
        subject = f"Накладная на заказ №{order.id}"

        result = send_mail(
            subject=subject,
            message='',  # Только HTML-формат письма
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_message,
            fail_silently=False
        )

        if result > 0:
            logger.info(f"Накладная успешно отправлена администратору на {admin_email}")
        else:
            logger.warning(f"Ошибка отправки накладной на {admin_email}: результат отправки равен {result}")

    except Order.DoesNotExist:
        logger.error(f"Заказ с номером {order_id} не найден!")
    except Exception as exc:
        logger.exception(f"Ошибка при отправке накладной: {exc}")


@shared_task(name="send_customer_order_confirmation_email")
def send_customer_order_confirmation_email(order_id):
    """
    Задача отправляет подтверждение заказа клиенту.
    """
    try:
        order = Order.objects.get(pk=order_id)
        customer_email = order.user.email
        subject = f"Ваш заказ №{order.id} подтвержден!"
        message = render_to_string('emails/customer_order_confirmation.html', {'order': order})
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer_email],
            fail_silently=False
        )
    except Order.DoesNotExist:
        pass


@shared_task(name="send_registration_confirmation_email")
def send_registration_confirmation_email(user_id):
    """
    Задача отправляет письмо с подтверждением регистрации новому пользователю.
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
        confirmation_link = f"{settings.SITE_URL}/api/v1/confirm-registration/{user.id}/{user.generate_confirmation_token()}/"

        message_body = (
            f"ДОБРО ПОЖАЛОВАТЬ!\n\n"
            f"ВЫ УСПЕШНО ЗАРЕГИСТРИРОВАЛИСЬ НА НАШЕМ СЕРВИСЕ ЗАКУПОК.\n\n"
            f"Для завершения регистрации перейдите по следующей ссылке:\n"
            f"{confirmation_link}\n\n"
            f"С уважением,\n"
            f"Команда нашего сервиса."
        )

        send_mail(
            subject=f"Регистрация завершена",
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

    except CustomUser.DoesNotExist:
        pass