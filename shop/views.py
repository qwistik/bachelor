from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Order, OrderItem

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

# --- МАГАЗИН ТА КОРЗИНА ---
@login_required(login_url='/login/')
def product_list(request):
    products = Product.objects.all()

    # Замість .products використовуємо .items (related_name з моделі CartItem)
    # І дістаємо саме product_id з кожного CartItem
    cart_product_ids = request.user.cart.items.values_list('product_id', flat=True)

    return render(request, 'shop/index.html', {
        'products': products,
        'cart_product_ids': cart_product_ids
    })

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Шукаємо, чи є вже такий товар у корзині
    cart_item, created = CartItem.objects.get_or_create(cart=request.user.cart, product=product)

    if not created:
        # Якщо товар вже був, просто збільшуємо кількість
        cart_item.quantity += 1
        cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

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