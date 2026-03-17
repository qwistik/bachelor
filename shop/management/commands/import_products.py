import requests
from django.core.management.base import BaseCommand
from shop.models import Product


class Command(BaseCommand):
    help = 'Скачує товари з DummyJSON та зберігає в базу'

    def handle(self, *args, **kwargs):
        url = "https://dummyjson.com/products/category/mobile-accessories"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])

            count = 0
            for item in products:
                # update_or_create запобігає дублюванню товарів, якщо запустити скрипт двічі
                obj, created = Product.objects.update_or_create(
                    title=item['title'],
                    defaults={
                        'description': item['description'],
                        'price': item['price'],
                        'thumbnail': item['thumbnail'],
                        'brand': item.get('brand', 'Unknown')
                    }
                )
                if created:
                    count += 1

            self.stdout.write(self.style.SUCCESS(f'Успішно додано {count} нових товарів!'))
        else:
            self.stdout.write(self.style.ERROR('Помилка доступу до API'))