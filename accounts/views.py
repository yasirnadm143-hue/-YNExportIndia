from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import get_user_model

from .models import (
    Product,
    Order,
    Wallet,
    RechargeRequest,
    ReferralIncome,
)

from .forms import (
    CustomUserRegistrationForm,
    ProductForm,
)

User = get_user_model()


def home_view(request):
    query = request.GET.get("q", "")

    if query:
        products = Product.objects.filter(title__icontains=query)
    else:
        products = Product.objects.all()

    return render(
        request,
        "accounts/home.html",
        {
            "products": products,
            "query": query,
        },
    )


def register_step1(request):

    ref = request.GET.get("ref")

    if request.method == "POST":

        form = CustomUserRegistrationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            user = form.save(commit=False)

            if ref:
                try:
                    user.upline = User.objects.get(referral_id=ref)
                except User.DoesNotExist:
                    pass

            user.save()

            Wallet.objects.create(user=user)

            login(request, user)

            messages.success(
                request,
                "Registration Successful."
            )

            return redirect("dashboard")

    else:
        form = CustomUserRegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )
@login_required
def user_dashboard(request):

    orders = Order.objects.filter(user=request.user)

    referral_count = User.objects.filter(
        upline=request.user
    ).count()

    wallet, created = Wallet.objects.get_or_create(
        user=request.user
    )

    referral_income = ReferralIncome.objects.filter(
        user=request.user
    )

    total_income = sum(
        i.commission_amount
        for i in referral_income
    )

    if referral_count == 0:
        rank = "Starter"

    elif referral_count >= 1:
        rank = "Rank 20"

    elif referral_count >= 2:
        rank = "Rank 30"

    elif referral_count >= 5:
        rank = "Silver"

    elif referral_count >= 10:
        rank = "Gold"

    elif referral_count >= 20:
        rank = "Diamond"

    else:
        rank = "Starter"

    context = {
        "orders": orders,
        "wallet": wallet,
        "rank": rank,
        "referral_count": referral_count,
        "referral_income": total_income,
        "referral_id": request.user.referral_id,
        "referral_link": request.user.referral_link,
        "upline": request.user.upline,
    }

    return render(
        request,
        "accounts/dashboard.html",
        context
    )


@login_required
def wallet_view(request):

    wallet, created = Wallet.objects.get_or_create(
        user=request.user
    )

    recharges = RechargeRequest.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "accounts/wallet.html",
        {
            "wallet": wallet,
            "recharges": recharges,
        }
    )


@login_required
def customer_support(request):
    return render(request, "accounts/support.html")


@login_required
def user_settings(request):
    return render(request, "accounts/settings.html")


def product_detail(request, pk):

    product = get_object_or_404(Product, pk=pk)

    return render(
        request,
        "accounts/product_detail.html",
        {
            "product": product,
        },
    )
@login_required
def order_product(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":

        quantity = int(request.POST.get("quantity", 1))
        total_price = product.price * quantity

        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            total_price=total_price,
            full_name=request.POST.get("full_name"),
            mobile_number=request.POST.get("mobile_number"),
            address=request.POST.get("address"),
            district=request.POST.get("district"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
            status="Pending",
        )

        messages.success(
            request,
            "Order placed successfully."
        )

        return redirect(
            "payment_success",
            order_id=order.id
        )

    return render(
        request,
        "accounts/order_product.html",
        {
            "product": product,
        },
    )


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
            "order": order,
        },
    )


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
            "order": order,
        },
    )


@login_required
def upload_product(request):

    if not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()
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
            "form": form,
        },
    )


def register_verify_otp(request):
    return render(
        request,
        "accounts/verify_otp.html"
    )


def register_complete(request):
    return redirect("dashboard")


@login_required
def user_profile(request):
    return redirect("dashboard")
