import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.core.cache import cache


def smart_search(query_text, queryset):
    if not query_text:
        return queryset

    query_text = query_text.lower()

    # 1. Екстракція цінових фільтрів
    less_than = re.search(r'(?:до|менше|дешевше|under|below|max)\s*(\d+)', query_text)
    more_than = re.search(r'(?:від|більше|дорожче|over|above|min)\s*(\d+)', query_text)
    approx = re.search(r'(?:біля|близько|приблизно|around|about)\s*(\d+)', query_text)

    # Очищення запиту
    clean_query = re.sub(
        r'(?:до|від|менше|більше|дешевше|дорожче|біля|близько|приблизно|under|over|around|about|max|min)\s*\d+.*',
        '', query_text).strip()

    # 2. Фільтрація QuerySet за ціною (швидка операція БД)
    if less_than:
        queryset = queryset.filter(price__lte=int(less_than.group(1)))
    if more_than:
        queryset = queryset.filter(price__gte=int(more_than.group(1)))
    if approx:
        target_price = int(approx.group(1))
        queryset = queryset.filter(price__range=(target_price * 0.8, target_price * 1.2))

    # 3. Швидка перевірка
    if not queryset.exists() or not clean_query:
        return queryset

    # 4. Оптимізована IR-модель з кешуванням
    # Використовуємо кеш, щоб не перераховувати матрицю для всіх 500+ товарів щоразу
    cache_key = 'global_product_vector_data'
    cached_data = cache.get(cache_key)

    if cached_data:
        vectorizer, full_tfidf_matrix, all_ids = cached_data
    else:
        # Цей блок виконається лише один раз на годину
        from .models import Product
        all_products = Product.objects.all()
        texts = [f"{p.title} {p.brand} {p.description}" for p in all_products]
        all_ids = list(all_products.values_list('id', flat=True))

        vectorizer = TfidfVectorizer(max_features=1000)
        full_tfidf_matrix = vectorizer.fit_transform(texts)

        cache.set(cache_key, (vectorizer, full_tfidf_matrix, all_ids), 3600)

    # 5. Пошук збігів
    query_vector = vectorizer.transform([clean_query])
    cosine_sim = cosine_similarity(query_vector, full_tfidf_matrix).flatten()

    # Отримуємо ID топ-10 найбільш схожих товарів
    related_indices = cosine_sim.argsort()[-10:][::-1]
    top_ids = [all_ids[i] for i in related_indices if cosine_sim[i] > 0.1]

    # Повертаємо відфільтрований queryset, що містить тільки знайдені ID
    return queryset.filter(id__in=top_ids)