from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Cart, CartItem, Order, OrderItem
from .utils import smart_search
from .forms import ProductForm

from django.core.paginator import Paginator

# --- АВТОРИЗАЦІЯ ---
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # Створює юзера, а сигнал автоматично створює йому Корзину і Профіль
            login(request, user) # Одразу авторизуємо
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    in_cart = False
    if request.user.is_authenticated:
        in_cart = request.user.cart.items.filter(product=product).exists()

    return render(request, 'shop/product_detail.html', {'product': product, 'in_cart': in_cart})

# --- МАГАЗИН ТА КОРЗИНА ---
@login_required(login_url='/login/')
@login_required(login_url='/login/')
def product_list(request):
    query = request.GET.get('q', '').strip()
    use_smart = request.GET.get('use_smart') == 'on'
    products = Product.objects.all()

    if query:
        if use_smart:
            products = smart_search(query, products)
        else:
            results = products.filter(Q(title__icontains=query) | Q(brand__icontains=query))
            if not results.exists():
                products = smart_search(query, products)
            else:
                products = results

    # --- ПАГІНАЦІЯ (50 товарів на сторінку) ---
    paginator = Paginator(products, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    cart_product_ids = []
    if request.user.is_authenticated:
        cart_product_ids = request.user.cart.items.values_list('product_id', flat=True)

    return render(request, 'shop/index.html', {
        'products': page_obj, # Тепер передаємо лише 1 сторінку (50 товарів) замість усіх
        'cart_product_ids': cart_product_ids,
        'query': query,
        'use_smart': use_smart
    })


@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(cart=request.user.cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Повертаємо користувача на те саме місце, де він був
    referer = request.META.get('HTTP_REFERER')
    if referer:
        # Відрізаємо старий якір (якщо він є), щоб уникнути дублювання
        base_url = referer.split('#')[0]
        return redirect(f"{base_url}#product-{product_id}")

    return redirect('product_list')

@login_required(login_url='/login/')
def cart_detail(request):
    cart = request.user.cart
    items = cart.items.all()  # Тепер беремо CartItem, а не Product
    total_price = sum(item.total_price() for item in items)

    return render(request, 'shop/cart.html', {'items': items, 'total_price': total_price})

@login_required(login_url='/login/')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.cart)
    item.delete()
    return redirect('cart_detail')

@login_required
def product_edit(request, product_id=None):
    # Тільки для адмінів
    if not request.user.is_staff:
        return redirect('product_list')

    if product_id:
        product = get_object_or_404(Product, id=product_id)
    else:
        product = None

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'shop/product_form.html', {'form': form, 'product': product})

@login_required
def product_delete(request, product_id):
    if not request.user.is_staff:
        return redirect('product_list')
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('product_list')

@login_required(login_url='/login/')
def update_quantity(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.cart)

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
        item.save()

    return redirect('cart_detail')

@login_required(login_url='/login/')
def checkout(request):
    if request.method == 'POST':
        cart = request.user.cart
        items = cart.items.all() # Тепер беремо елементи корзини (CartItem)

        # Перевірка, щоб не створювати порожні замовлення
        if not items.exists():
            return redirect('product_list')

        total_price = sum(item.total_price() for item in items)

        # 1. Створюємо Замовлення
        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )

        # 2. Переносимо товари з корзини в OrderItem (із правильною кількістю!)
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity # Тепер зберігаємо правильну кількість товару
            )

        # 3. Очищаємо корзину (видаляємо всі CartItem для цієї корзини)
        items.delete()

        return render(request, 'shop/checkout_success.html')

    return redirect('cart_detail')