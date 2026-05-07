from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),

    # Авторизація
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Корзина та замовлення
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # зміна кількості товарів (+ та -)
    path('cart/update/<int:item_id>/<str:action>/', views.update_quantity, name='update_quantity'),

    path('checkout/', views.checkout, name='checkout'),

    # адмін
    path('product/add/', views.product_edit, name='product_add'), # Створення нового (без ID)
    path('product/<int:product_id>/edit/', views.product_edit, name='product_edit'), # Редагування
    path('product/<int:product_id>/delete/', views.product_delete, name='product_delete'), # Видалення
]