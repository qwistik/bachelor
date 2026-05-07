import csv
from django.http import HttpResponse
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, UserProfile, Cart, Order, OrderItem

# --- Кастомні дії (Actions) ---

@admin.action(description='Вивантажити обрані замовлення у CSV')
def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID Замовлення', 'Користувач', 'Сума ($)', 'Дата та час'])

    for order in queryset:
        date_formatted = order.created_at.strftime('%Y-%m-%d %H:%M')
        writer.writerow([order.id, order.user.username, order.total_price, date_formatted])
    return response

# --- Вкладені відображення (Inlines) ---

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity']

# --- Реєстрація моделей (ModelAdmins) ---

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Відображаємо маленьке фото, назву, ціну та бренд у списку
    list_display = ['show_photo', 'title', 'price_display', 'brand']
    # Можливість редагувати бренд та ціну прямо у списку (дуже зручно для адміна)
    list_editable = ['brand']
    # Пошук та фільтрація
    search_fields = ['title', 'brand']
    list_filter = ['brand']
    list_per_page = 20

    # Покращене групування полів при створенні/редагуванні
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'brand', 'price')
        }),
        ('Контент та медіа', {
            'fields': ('description', 'thumbnail'),
        }),
    )

    # Кастомні методи для відображення HTML в адмінці
    def show_photo(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="width: 50px; height: auto; border-radius: 5px;" />', obj.thumbnail)
        return "Немає фото"
    show_photo.short_description = 'Фото'

    def price_display(self, obj):
        return format_html('<b style="color: #28a745;">${}</b>', obj.price)
    price_display.short_description = 'Ціна'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'created_at']
    list_filter = ['created_at', 'user']
    inlines = [OrderItemInline]
    actions = [export_to_csv]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'language', 'text_size']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user']