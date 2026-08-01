from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product

def home_view(request):
    products = Product.objects.all()
    return render(request, 'accounts/home.html', {'products': products})

@login_required
def user_dashboard(request):
    return render(request, 'accounts/dashboard.html')

@login_required
def user_profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def user_settings(request):
    return render(request, 'accounts/settings.html')

@login_required
def wallet_view(request):
    return render(request, 'accounts/wallet.html')

def customer_support(request):
    return render(request, 'accounts/support.html')

@login_required
def track_order(request, order_id):
    return render(request, 'accounts/track_order.html', {'order_id': order_id})

@login_required
def payment_success(request, order_id):
    return render(request, 'accounts/payment_success.html', {'order_id': order_id})

def register_step1(request):
    return render(request, 'accounts/register.html')

def register_verify_otp(request):
    return render(request, 'accounts/verify_otp.html')

def register_complete(request):
    return render(request, 'accounts/register_complete.html')

def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'accounts/product_detail.html', {'product': product})

@login_required
def order_product(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'accounts/order_product.html', {'product': product})

@login_required
def upload_product(request):
    return render(request, 'accounts/upload_product.html')
