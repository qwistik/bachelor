import os
import django
import random
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shop.models import Product

fake = Faker()


def generate_accessories(n=2500):
    categories = ['Годинник', 'Чохол', 'Окуляри', 'Браслет', 'Навушники', 'Провод', 'Поп-сокет']
    brands = ['Apple', 'Samsung', 'Xiaomi', 'Oppo', 'Casio', 'Google', 'Microsoft']

    print(f"Починаю генерацію {n} товарів...")

    for i in range(n):
        brand = random.choice(brands)
        category = random.choice(categories)
        title = f"{brand} {category} {fake.word().capitalize()} {random.randint(100, 999)}"

        Product.objects.create(
            title=title,
            description=fake.paragraph(nb_sentences=3),
            price=round(random.uniform(10.0, 500.0), 2),
            thumbnail=f"https://picsum.photos/seed/{i}/300/300",  # Використовуємо безкоштовні заглушки фото
            brand=brand
        )

        if (i + 1) % 100 == 0:
            print(f"Створено {i + 1} товарів...")

    print("Генерація завершена успішно!")


if __name__ == '__main__':
    generate_accessories(2500)