from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Product, Cart

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
    return render(request, 'shop/index.html', {'products': products})

@login_required(login_url='/login/')
def cart_detail(request):
    cart = request.user.cart
    products = cart.products.all() # Беремо всі товари з корзини
    total_price = sum(item.price for item in products) # Рахуємо загальну суму
    return render(request, 'shop/cart.html', {'products': products, 'total_price': total_price})

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.user.cart.products.add(product) # Додаємо товар у корзину
    return redirect('cart_detail') # Переходимо в корзину

@login_required(login_url='/login/')
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.user.cart.products.remove(product) # Видаляємо товар з корзини
    return redirect('cart_detail')