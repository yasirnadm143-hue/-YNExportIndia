from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Product, Order

User = get_user_model()

def home_view(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(title__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'accounts/home.html', {'products': products, 'query': query})

@login_required
def upload_product(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        
        if not title or not price:
            messages.error(request, "Product title and price are required!")
            return redirect('upload_product')
            
        Product.objects.create(title=title, price=price, image=image)
        messages.success(request, "Product uploaded successfully!")
        return redirect('home')
        
    return render(request, 'accounts/upload_product.html')

@login_required
def user_dashboard(request):
    referral_count = User.objects.filter(upline=request.user).count() if hasattr(User, 'upline') else 0
    if referral_count >= 20:
        request.user.rank = 'Diamond Leader 💎'
    elif referral_count >= 10:
        request.user.rank = 'Gold Achiever 🥇'
    elif referral_count >= 5:
        request.user.rank = 'Silver Partner 🥈'
    else:
        request.user.rank = 'Bronze Member 🥉'
    try:
        request.user.save()
    except Exception:
        pass
    orders = Order.objects.filter(user=request.user)
    return render(request, 'accounts/dashboard.html', {'referral_count': referral_count, 'orders': orders})

@login_required
def wallet_view(request):
    return render(request, 'accounts/wallet.html')

@login_required
def customer_support(request):
    return render(request, 'accounts/support.html')

@login_required
def user_settings(request):
    return render(request, 'accounts/settings.html')

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'accounts/product_detail.html', {'product': product})

@login_required
def order_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        total_price = product.price * quantity
        order = Order.objects.create(
            user=request.user, product=product, quantity=quantity,
            total_price=total_price, status='Order Placed',
            address=request.POST.get('address', ''),
            district=request.POST.get('district', ''),
            state=request.POST.get('state', ''),
            pincode=request.POST.get('pincode', '')
        )
        return redirect('payment_success', order_id=order.id)
    return render(request, 'accounts/order_product.html', {'product': product})

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'accounts/payment_success.html', {'order': order})

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'accounts/track_order.html', {'order': order})

def register_step1(request):
    return render(request, 'accounts/register.html')

def register_verify_otp(request):
    return render(request, 'accounts/verify_otp.html')

def register_complete(request):
    return redirect('home')

def user_profile(request):
    return redirect('dashboard')
