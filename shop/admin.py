import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Product, UserProfile, Cart, Order, OrderItem

# --- Кастомні дії (Actions) ---

@admin.action(description='Вивантажити обрані замовлення у CSV')
def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_report.csv"'

    writer = csv.writer(response)
    # Заголовки колонок у файлі
    writer.writerow(['ID Замовлення', 'Користувач', 'Сума ($)', 'Дата та час'])

    # Заповнення даними
    for order in queryset:
        date_formatted = order.created_at.strftime('%Y-%m-%d %H:%M')
        writer.writerow([order.id, order.user.username, order.total_price, date_formatted])

    return response

# --- Вкладені відображення (Inlines) ---

class OrderItemInline(admin.TabularInline):
    """Дозволяє бачити товари прямо всередині сторінки конкретного замовлення"""
    model = OrderItem
    extra = 0 # Прибирає зайві порожні рядки для додавання нових товарів
    readonly_fields = ['product', 'price', 'quantity'] # Забороняє випадково змінювати історію покупок

# --- Реєстрація моделей (ModelAdmins) ---

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'created_at']
    list_filter = ['created_at']
    inlines = [OrderItemInline]
    actions = [export_to_csv] # Підключення нашого експорту

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Відображення колонок у загальному списку товарів
    list_display = ['title', 'price', 'brand']
    # Додає панель пошуку за назвою та брендом
    search_fields = ['title', 'brand']
    # Додає бокову панель для фільтрації товарів за брендом
    list_filter = ['brand']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'language', 'text_size']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user']