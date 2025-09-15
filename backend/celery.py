"""
Файл настроек Celery
https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html
"""
from __future__ import absolute_import
import os
from celery import Celery

# этот код скопирован с manage.py
# он установит модуль настроек по умолчанию Django для приложения 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# здесь вы меняете имя
app = Celery("backend")

# Для получения настроек Django, связываем префикс "CELERY" с настройкой celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# загрузка tasks.py в приложение django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


