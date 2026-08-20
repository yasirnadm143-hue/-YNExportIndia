from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Order
from .forms import ProductForm, OrderForm


# ==========================
# HOME
# ==========================

def home_view(request):
    products = Product.objects.all()
    return render(request, "accounts/home.html", {
        "products": products
    })


# ==========================
# DASHBOARD
# ==========================

@login_required
def user_dashboard(request):
    return render(request, "accounts/dashboard.html")


@login_required
def user_profile(request):
    return render(request, "accounts/profile.html")


@login_required
def user_settings(request):
    return render(request, "accounts/settings.html")


@login_required
def wallet_view(request):
    return render(request, "accounts/wallet.html")


def customer_support(request):
    return render(request, "accounts/support.html")


# ==========================
# REGISTER
# ==========================

def register_step1(request):
    return render(request, "accounts/register.html")


def register_verify_otp(request):
    return render(request, "accounts/verify_otp.html")


def register_complete(request):
    return render(request, "accounts/register_complete.html")
# ==========================
# PRODUCT DETAILS
# ==========================

def product_detail(request, pk):

    product = get_object_or_404(Product, pk=pk)

    return render(
        request,
        "accounts/product_detail.html",
        {
            "product": product
        }
    )


# ==========================
# UPLOAD PRODUCT
# ==========================

@login_required
def upload_product(request):

    if not request.user.is_staff:
        messages.error(request, "Only Admin can upload products.")
        return redirect("home")

    if request.method == "POST":

        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():

            product = form.save(commit=False)
            product.owner = request.user
            product.save()

            messages.success(request, "Product uploaded successfully.")
            return redirect("home")

    else:

        form = ProductForm()

    return render(
        request,
        "accounts/upload_product.html",
        {
            "form": form
        }
    )
# ==========================
# EDIT PRODUCT
# ==========================

@login_required
def edit_product(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if not (request.user.is_staff or product.owner == request.user):
        messages.error(request, "You are not allowed to edit this product.")
        return redirect("home")

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("product_detail", pk=product.id)

    else:

        form = ProductForm(instance=product)

    return render(
        request,
        "accounts/upload_product.html",
        {
            "form": form,
            "product": product
        }
    )


# ==========================
# DELETE PRODUCT
# ==========================

@login_required
def delete_product(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if not (request.user.is_staff or product.owner == request.user):
        messages.error(request, "You are not allowed to delete this product.")
        return redirect("home")

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("home")

    return render(
        request,
        "accounts/delete_product.html",
        {
            "product": product
        }
    )
# ==========================
# ORDER PRODUCT
# ==========================

@login_required
def order_product(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":

        form = OrderForm(request.POST)

        if form.is_valid():

            order = form.save(commit=False)
            order.product = product
            order.user = request.user
            order.save()

            messages.success(request, "Order placed successfully.")

            return redirect("payment_success", order_id=order.id)

    else:

        form = OrderForm()

    return render(
        request,
        "accounts/order_product.html",
        {
            "product": product,
            "form": form
        }
    )


# ==========================
# PAYMENT SUCCESS
# ==========================

@login_required
def payment_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "accounts/payment_success.html",
        {
            "order": order
        }
    )


# ==========================
# TRACK ORDER
# ==========================

@login_required
def track_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "accounts/track_order.html",
        {
            "order": order
        }
    )
