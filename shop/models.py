from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. Модель товару (сюди ми збережемо дані з API)
class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    thumbnail = models.URLField(verbose_name="Фото URL")
    brand = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title

# 2. Модель профілю (для налаштувань: мова, валюта, розмір тексту)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, default='UAH', choices=[('UAH', 'Гривня'), ('USD', 'Долар')])
    language = models.CharField(max_length=2, default='uk', choices=[('uk', 'Українська'), ('en', 'English')])
    text_size = models.CharField(max_length=10, default='medium', choices=[('small', 'Дрібний'), ('medium', 'Середній'), ('large', 'Великий')])

    def __str__(self):
        return f"Профіль {self.user.username}"

# 3. Модель корзини
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f"Корзина {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile_and_cart(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        Cart.objects.create(user=instance)