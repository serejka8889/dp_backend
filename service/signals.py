from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Cart

@receiver(post_save, sender=CustomUser)
def create_cart(sender, instance, created, **kwargs):
    """
    Создаёт корзину для пользователя при его регистрации.
    """
    if created:
        Cart.objects.create(user=instance)