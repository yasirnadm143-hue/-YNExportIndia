from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login

from .models import Product, Order, CustomUser
from .forms import ProductForm, OrderForm


# ==========================
# HOME
# ==========================

def home_view(request):
    products = Product.objects.all()

    return render(
        request,
        "accounts/home.html",
        {
            "products": products
        }
    )


# ==========================
# DASHBOARD
# ==========================

@login_required
def user_dashboard(request):
    return render(
        request,
        "accounts/dashboard.html"
    )


# ==========================
# PROFILE
# ==========================

@login_required
def user_profile(request):
    return render(
        request,
        "accounts/profile.html"
    )


# ==========================
# SETTINGS
# ==========================

@login_required
def user_settings(request):
    return render(
        request,
        "accounts/settings.html"
    )


# ==========================
# WALLET
# ==========================

@login_required
def wallet_view(request):
    return render(
        request,
        "accounts/wallet.html"
    )


# ==========================
# CUSTOMER SUPPORT
# ==========================

def customer_support(request):
    return render(
        request,
        "accounts/support.html"
    )


# ==========================
# REGISTER
# ==========================

def register_step1(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        referral_id = request.POST.get("referral_id", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        errors = []

        # Required fields
        if not username:
            errors.append("Username is required.")

        if not first_name:
            errors.append("First name is required.")

        if not last_name:
            errors.append("Last name is required.")

        if not email:
            errors.append("Email is required.")

        if not phone_number:
            errors.append("Mobile number is required.")

        if not password:
            errors.append("Password is required.")

        # Password confirmation
        if password and password != password2:
            errors.append("Passwords do not match.")

        # Username check
        if username and CustomUser.objects.filter(
            username__iexact=username
        ).exists():
            errors.append("This username is already registered.")

        # Email check
        if email and CustomUser.objects.filter(
            email__iexact=email
        ).exists():
            errors.append("This email is already registered.")

        # Phone check
        if phone_number and CustomUser.objects.filter(
            phone_number=phone_number
        ).exists():
            errors.append("This mobile number is already registered.")

        # Referral check
        upline = None

        if referral_id:

            upline = CustomUser.objects.filter(
                referral_id=referral_id
            ).first()

            if not upline:
                errors.append(
                    "Invalid Referral ID."
                )

        # If errors exist
        if errors:

            for error in errors:
                messages.error(request, error)

            return render(
                request,
                "accounts/register.html",
                {
                    "form_data": request.POST
                }
            )

        # Create user
        user = CustomUser(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            upline=upline,
        )

        # Password hashing
        user.set_password(password)

        # Save user
        user.save()

        messages.success(
            request,
            "Registration successful. You can now login."
        )

        return redirect("login")

    return render(
        request,
        "accounts/register.html"
    )


# ==========================
# OTP VERIFICATION PAGE
# ==========================

def register_verify_otp(request):

    return render(
        request,
        "accounts/register_verify_otp.html"
    )


# ==========================
# REGISTRATION COMPLETE
# ==========================

def register_complete(request):

    return render(
        request,
        "accounts/register_complete.html"
    )


# ==========================
# PRODUCT DETAILS
# ==========================

def product_detail(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

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

        messages.error(
            request,
            "Only Admin can upload products."
        )

        return redirect("home")

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            product = form.save(
                commit=False
            )

            product.owner = request.user
            product.save()

            messages.success(
                request,
                "Product uploaded successfully."
            )

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

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if not (
        request.user.is_staff
        or product.owner == request.user
    ):

        messages.error(
            request,
            "You are not allowed to edit this product."
        )

        return redirect("home")

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Product updated successfully."
            )

            return redirect(
                "product_detail",
                pk=product.id
            )

    else:

        form = ProductForm(
            instance=product
        )

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

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if not (
        request.user.is_staff
        or product.owner == request.user
    ):

        messages.error(
            request,
            "You are not allowed to delete this product."
        )

        return redirect("home")

    if request.method == "POST":

        product.delete()

        messages.success(
            request,
            "Product deleted successfully."
        )

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

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == "POST":

        form = OrderForm(
            request.POST
        )

        if form.is_valid():

            order = form.save(
                commit=False
            )

            order.product = product
            order.user = request.user

            order.save()

            messages.success(
                request,
                "Order placed successfully."
            )

            return redirect(
                "payment_success",
                order_id=order.id
            )

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
