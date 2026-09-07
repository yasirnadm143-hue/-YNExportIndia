from decimal import Decimal, InvalidOperation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
import os

from .models import (
    Product,
    Order,
    CustomUser,
    Notification,
    SupportTicket,
    SupportMessage,
)
from .forms import ProductForm, OrderForm



# ==========================
# ONE-TIME ADMIN SETUP
# ==========================

@require_http_methods(["GET", "POST"])
def one_time_admin_setup(request):

    User = get_user_model()
    setup_key = os.environ.get("ADMIN_SETUP_KEY")

    if not setup_key:
        return render(
            request,
            "accounts/admin_setup.html",
            {"error": "Admin setup is disabled."},
            status=404,
        )

    # Permanently lock this page after the first superuser exists.
    if User.objects.filter(is_superuser=True).exists():
        return render(
            request,
            "accounts/admin_setup.html",
            {"locked": True},
            status=403,
        )

    if request.method == "POST":

        submitted_key = request.POST.get("setup_key", "")
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if submitted_key != setup_key:
            return render(
                request,
                "accounts/admin_setup.html",
                {"error": "Invalid setup key."},
                status=403,
            )

        if not username or not password:
            return render(
                request,
                "accounts/admin_setup.html",
                {"error": "Username and password are required."},
            )

        if password != password2:
            return render(
                request,
                "accounts/admin_setup.html",
                {"error": "Passwords do not match."},
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "accounts/admin_setup.html",
                {"error": "Username already exists."},
            )

        user = User(
            username=username,
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )

        user.set_password(password)
        user.save()

        return render(
            request,
            "accounts/admin_setup.html",
            {
                "success": True,
                "username": username,
            },
        )

    return render(
        request,
        "accounts/admin_setup.html",
    )

# ==========================
# HOME
# ==========================

def home_view(request):
    from django.db.models import Q

    query = (request.GET.get("q") or "").strip()

    products = Product.objects.all()

    if query:
        # Normalize the search text
        words = [
            word.strip()
            for word in query.split()
            if word.strip()
        ]

        # Match the complete query first
        search_filter = (
            Q(title__icontains=query)
            | Q(category__name__icontains=query)
            | Q(description__icontains=query)
        )

        # Also allow multi-word searches.
        # Example: "black shirt" can match products
        # containing "black" and "shirt".
        for word in words:
            search_filter |= (
                Q(title__icontains=word)
                | Q(category__name__icontains=word)
                | Q(description__icontains=word)
            )

        products = products.filter(
            search_filter
        ).distinct()

    return render(
        request,
        "accounts/home.html",
        {
            "products": products,
            "query": query,
        }
    )

# ==========================
# DASHBOARD
# ==========================

@login_required
def user_dashboard(request):

    user = request.user

    # Direct team
    direct_team = CustomUser.objects.filter(
        upline=user
    ).count()

    # Total team: all levels below the current user
    total_team = 0
    current_level = [user]
    visited = {user.id}

    while current_level:
        next_level = list(
            CustomUser.objects.filter(
                upline__in=current_level
            ).exclude(
                id__in=visited
            )
        )

        if not next_level:
            break

        total_team += len(next_level)

        visited.update(
            member.id for member in next_level
        )

        current_level = next_level

    # MLM commission income
    from django.db.models import Sum
    from .models import CommissionTransaction

    total_income = CommissionTransaction.objects.filter(
        beneficiary=user
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    referral_link = request.build_absolute_uri(
        "/register/"
    ) + "?ref=" + str(user.referral_id)

    return render(
        request,
        "accounts/dashboard.html",
        {
            "user": user,
            "direct_team": direct_team,
            "total_team": total_team,
            "referral_count": total_team,
            "total_income": total_income,
            "referral_link": referral_link,
        }
    )


# ==========================
# MLM COMMISSION
# ==========================

@login_required
def mlm_commission_view(request):
    """
    Complete MLM commission dashboard.

    Shows:
    - total commission
    - transaction count
    - level-wise commission
    - commission history
    - source user
    - order/product information
    - order/tracking information
    - direct downline
    """

    from django.db.models import Sum
    from .models import CommissionTransaction

    user = request.user

    transactions = (
        CommissionTransaction.objects
        .filter(beneficiary=user)
        .select_related(
            "source_user",
            "order",
            "order__product",
        )
        .order_by("-created_at")
    )

    total_commission = (
        transactions.aggregate(
            total=Sum("amount")
        )["total"] or 0
    )

    level_summary = (
        transactions
        .values("level")
        .annotate(total=Sum("amount"))
        .order_by("level")
    )

    direct_downline = (
        CustomUser.objects
        .filter(upline=user)
        .order_by("date_joined")
    )

    return render(
        request,
        "accounts/mlm_commission.html",
        {
            "user": user,
            "transactions": transactions,
            "level_summary": level_summary,
            "total_commission": total_commission,
            "direct_downline": direct_downline,
            "transaction_count": transactions.count(),
        },
    )


@login_required
def download_commission_csv(request):
    """
    Download logged-in user's complete MLM commission history as CSV.
    """

    import csv
    from django.http import HttpResponse
    from .models import CommissionTransaction

    transactions = (
        CommissionTransaction.objects
        .filter(beneficiary=request.user)
        .select_related(
            "source_user",
            "order",
            "order__product",
        )
        .order_by("-created_at")
    )

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )

    response["Content-Disposition"] = (
        'attachment; filename="YN-Commerce-Commission-History.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Status",
        "Date",
        "Level",
        "Source User",
        "Product",
        "Order ID",
        "Tracking ID",
        "Order Amount",
        "Commission Rate",
        "Commission Amount",
    ])

    for transaction in transactions:

        order = transaction.order

        writer.writerow([
            "CREDITED",
            transaction.created_at.strftime(
                "%d-%m-%Y %H:%M:%S"
            ) if transaction.created_at else "",
            transaction.level,
            transaction.source_user.username
            if transaction.source_user else "",
            order.product.title
            if order and order.product else "",
            order.id
            if order else "",
            order.tracking_id
            if order else "",
            transaction.order_amount,
            f"{transaction.rate * 100:.2f}%",
            transaction.amount,
        ])

    return response



# ==========================
# MLM COMMISSION HISTORY
# ==========================

@login_required
def mlm_commission_history_view(request):
    """
    Complete commission history for the logged-in user.
    Includes commission, order, product, source user and
    current order/payment status.
    """

    from django.db.models import Sum
    from .models import CommissionTransaction

    user = request.user

    transactions = (
        CommissionTransaction.objects
        .filter(beneficiary=user)
        .select_related(
            "source_user",
            "order",
            "order__product",
        )
        .order_by("-created_at")
    )

    total_commission = (
        transactions.aggregate(total=Sum("amount"))["total"]
        or 0
    )

    return render(
        request,
        "accounts/mlm_commission_history.html",
        {
            "user": user,
            "transactions": transactions,
            "total_commission": total_commission,
        },
    )


# ==========================
# DIRECT TEAM
# ==========================

@login_required
def direct_team_view(request):
    """
    Show all direct downline members of the logged-in user.
    """

    user = request.user

    direct_team = (
        CustomUser.objects
        .filter(upline=user)
        .order_by("date_joined")
    )

    return render(
        request,
        "accounts/direct_team.html",
        {
            "user": user,
            "direct_team": direct_team,
            "direct_team_count": direct_team.count(),
        },
    )


# ==========================
# TOTAL TEAM
# ==========================

@login_required
def total_team_view(request):
    """
    Show the complete downline network level-by-level.
    Maximum MLM depth displayed: 20 levels.
    """

    user = request.user

    levels = []
    current_level = [user]
    visited = {user.id}

    for level_number in range(1, 21):

        members = list(
            CustomUser.objects
            .filter(upline__in=current_level)
            .exclude(id__in=visited)
            .order_by("date_joined")
        )

        if not members:
            break

        visited.update(
            member.id for member in members
        )

        levels.append(
            {
                "number": level_number,
                "members": members,
                "count": len(members),
            }
        )

        current_level = members

    total_count = sum(
        level["count"]
        for level in levels
    )

    return render(
        request,
        "accounts/total_team.html",
        {
            "user": user,
            "levels": levels,
            "total_count": total_count,
        },
    )



# ==========================
# MY NETWORK / MLM TREE
# ==========================

@login_required
def mlm_tree_view(request):
    """
    Complete MLM network navigation.

    Supports:
    - direct downline
    - complete downline
    - level-wise team
    - upline navigation
    - downline navigation
    - direct team details
    - total team details
    """

    user = request.user

    selected_id = request.GET.get("user")

    selected_user = user

    # ------------------------------------------------------
    # BUILD USER'S COMPLETE OWN NETWORK
    # ------------------------------------------------------

    descendants = []
    current_level = [user]
    visited = {user.id}

    while current_level:

        next_level = list(
            CustomUser.objects
            .filter(upline__in=current_level)
            .exclude(id__in=visited)
            .order_by("date_joined")
        )

        if not next_level:
            break

        descendants.extend(next_level)

        visited.update(
            member.id
            for member in next_level
        )

        current_level = next_level

    descendant_ids = {
        member.id
        for member in descendants
    }

    # ------------------------------------------------------
    # BUILD UPLINE CHAIN
    # ------------------------------------------------------

    ancestors = []

    current = user.upline
    ancestor_seen = {user.id}

    while current and current.id not in ancestor_seen:

        ancestors.append(current)
        ancestor_seen.add(current.id)

        current = current.upline

    ancestor_ids = {
        member.id
        for member in ancestors
    }

    # ------------------------------------------------------
    # SELECT USER
    # ------------------------------------------------------

    if selected_id:

        try:
            candidate = CustomUser.objects.get(
                id=int(selected_id)
            )
        except (
            ValueError,
            TypeError,
            CustomUser.DoesNotExist,
        ):
            candidate = None

        if candidate:

            # User can navigate through:
            # 1. Own account
            # 2. Own downline
            # 3. Own upline chain

            if (
                candidate.id == user.id
                or candidate.id in descendant_ids
                or candidate.id in ancestor_ids
            ):
                selected_user = candidate

    # ------------------------------------------------------
    # DIRECT DOWNLINE
    # ------------------------------------------------------

    downlines = (
        CustomUser.objects
        .filter(upline=selected_user)
        .order_by("date_joined")
    )

    # ------------------------------------------------------
    # COMPLETE TEAM OF SELECTED USER
    # ------------------------------------------------------

    network_levels = []

    current_level = list(downlines)
    visited = {selected_user.id}

    team_members = []

    level_number = 1

    while current_level:

        level_members = []

        for member in current_level:

            if member.id in visited:
                continue

            visited.add(member.id)
            level_members.append(member)
            team_members.append(member)

        if level_members:

            network_levels.append({
                "level": level_number,
                "members": level_members,
                "count": len(level_members),
            })

        next_level = list(
            CustomUser.objects
            .filter(upline__in=level_members)
            .exclude(id__in=visited)
            .order_by("date_joined")
        )

        current_level = next_level
        level_number += 1

    total_team = len(team_members)

    # ------------------------------------------------------
    # SELECTED USER'S UPLINE
    # ------------------------------------------------------

    parent_user = selected_user.upline

    # ------------------------------------------------------
    # DIRECT TEAM COUNTS
    # ------------------------------------------------------

    direct_team_count = downlines.count()

    # ------------------------------------------------------
    # COMMISSION COUNT FOR SELECTED USER
    # ------------------------------------------------------

    from .models import CommissionTransaction

    commission_count = CommissionTransaction.objects.filter(
        beneficiary=selected_user
    ).count()

    # ------------------------------------------------------
    # ROOT / NAVIGATION INFO
    # ------------------------------------------------------

    is_root = selected_user.id == user.id

    return render(
        request,
        "accounts/mlm_tree.html",
        {
            "current_user": selected_user,
            "downlines": downlines,
            "total_team": total_team,
            "direct_team_count": direct_team_count,
            "team_members": team_members,
            "network_levels": network_levels,
            "parent_user": parent_user,
            "is_root": is_root,
            "commission_count": commission_count,
            "root_user": user,
        },
    )


# ==========================
# PROFILE

# ==========================

@login_required
def user_profile(request):

    user = request.user

    # Direct team
    direct_team = CustomUser.objects.filter(
        upline=user
    ).count()

    # Total team - all levels
    total_team = 0
    current_level = [user]
    visited = {user.id}

    while current_level:

        next_level = list(
            CustomUser.objects.filter(
                upline__in=current_level
            ).exclude(
                id__in=visited
            )
        )

        if not next_level:
            break

        total_team += len(next_level)

        visited.update(
            member.id for member in next_level
        )

        current_level = next_level

    # Referral link
    referral_link = request.build_absolute_uri(
        "/register/"
    ) + "?ref=" + str(user.referral_id)

    return render(
        request,
        "accounts/profile.html",
        {
            "user": user,
            "direct_team": direct_team,
            "total_team": total_team,
            "referral_link": referral_link,
        }
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
# BONUS BALANCE
# ==========================

@login_required
def bonus_balance_view(request):
    return render(
        request,
        "accounts/bonus_balance.html"
    )


# ==========================
# NOTIFICATIONS
# ==========================

@login_required
def notifications_view(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).select_related(
        "order"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "accounts/notifications.html",
        {
            "notifications": notifications
        }
    )


# ==========================
# CUSTOMER SUPPORT
# ==========================

# ==========================
# CUSTOMER SUPPORT
# ==========================

@login_required
@require_http_methods(["GET", "POST"])
def customer_support(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        errors = []

        if not email:
            errors.append("Email is required.")

        if not subject:
            errors.append("Subject is required.")

        if not message_text:
            errors.append("Please describe your problem.")

        if len(subject) > 200:
            errors.append("Subject is too long.")

        if errors:
            for error in errors:
                messages.error(request, error)

            return render(
                request,
                "accounts/support.html",
                {
                    "tickets": SupportTicket.objects.filter(
                        user=request.user
                    ).order_by("-created_at")
                }
            )

        # Always associate the ticket with the logged-in user.
        ticket = SupportTicket.objects.create(
            user=request.user,
            email=email,
            subject=subject,
            message=message_text,
            status="OPEN",
            priority="NORMAL",
        )

        # Save the original customer message separately.
        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message_text,
            is_staff_reply=False,
        )

        messages.success(
            request,
            f"Support ticket {ticket.ticket_id} created successfully."
        )

        return redirect("customer_support")

    tickets = SupportTicket.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "accounts/support.html",
        {
            "tickets": tickets,
        }
    )



# ==========================
# SUPPORT TICKET DETAIL
# ==========================

@login_required
@require_http_methods(["GET", "POST"])
def support_ticket_detail(request, ticket_id):

    ticket = get_object_or_404(
        SupportTicket,
        ticket_id=ticket_id,
        user=request.user,
    )

    if request.method == "POST":

        message_text = request.POST.get("message", "").strip()

        if not message_text:
            messages.error(
                request,
                "Please enter a message."
            )
            return redirect(
                "support_ticket_detail",
                ticket_id=ticket.ticket_id,
            )

        if ticket.status in ["RESOLVED", "CLOSED"]:
            messages.error(
                request,
                "This ticket is closed. Please create a new ticket."
            )
            return redirect(
                "support_ticket_detail",
                ticket_id=ticket.ticket_id,
            )

        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message_text,
            is_staff_reply=False,
        )

        ticket.status = "OPEN"
        ticket.save(update_fields=["status", "updated_at"])

        messages.success(
            request,
            "Your reply has been sent successfully."
        )

        return redirect(
            "support_ticket_detail",
            ticket_id=ticket.ticket_id,
        )

    ticket_messages = ticket.messages.select_related(
        "sender"
    ).all()

    return render(
        request,
        "accounts/support_ticket_detail.html",
        {
            "ticket": ticket,
            "ticket_messages": ticket_messages,
        }
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
        # Referral ID is OPTIONAL
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

            # ==========================
            # ORDER PAYMENT CALCULATION
            # ==========================

            product_amount = product.price
            delivery_charge = 45
            shopping_charge = 15

            total_amount = (
                product_amount
                + delivery_charge
                + shopping_charge
            )

            # 100% Cash on Delivery.
            online_payment_amount = 0
            cod_amount = total_amount

            order.product_amount = product_amount
            order.delivery_charge = delivery_charge
            order.shopping_charge = shopping_charge
            order.total_amount = total_amount
            order.online_payment_amount = online_payment_amount
            order.cod_amount = cod_amount

            # No online payment is required.
            order.payment_status = "PENDING"

            order.save()

            # ==========================
            # PAYMENT PENDING NOTIFICATION
            # ==========================

            Notification.objects.create(
                user=request.user,
                order=order,
                title="Order Confirmed",
                message=(
                    f"Order #{order.id} has been created successfully. "
                    f"Tracking ID: {order.tracking_id}. "
                    f"Payment will be collected in full at delivery "
                    f"through Cash on Delivery."
                )
            )

            messages.success(
                request,
                "Order placed successfully. Full payment will be collected "
                "at the time of delivery."
            )

            return redirect(
                "payment_success",
                order_id=order.id
            )

    else:

        form = OrderForm()

    # ==========================
    # PAYMENT PREVIEW FOR CUSTOMER
    # ==========================

    product_amount = product.price
    delivery_charge = 45
    shopping_charge = 15

    total_amount = (
        product_amount
        + delivery_charge
        + shopping_charge
    )

    online_payment_amount = 0
    cod_amount = total_amount

    return render(
        request,
        "accounts/order_product.html",
        {
            "product": product,
            "form": form,
            "product_amount": product_amount,
            "delivery_charge": delivery_charge,
            "shopping_charge": shopping_charge,
            "total_amount": total_amount,
            "online_payment_amount": online_payment_amount,
            "cod_amount": cod_amount,
        }
    )


# ==========================
# PAYMENT SUCCESS
# ==========================

@login_required
def download_invoice(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="YN-Exports-Invoice-{order.id}.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=A4
    )

    width, height = A4

    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(
        50,
        y,
        "YN COMMERCE INDIA"
    )

    y -= 35

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(
        50,
        y,
        "ORDER INVOICE"
    )

    y -= 30

    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        50,
        y,
        f"Order ID: #{order.id}"
    )

    y -= 18

    pdf.drawString(
        50,
        y,
        f"Tracking ID: {order.tracking_id}"
    )

    y -= 18

    pdf.drawString(
        50,
        y,
        f"Order Date: {order.created_at.strftime('%d-%m-%Y %H:%M')}"
    )

    y -= 30

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(
        50,
        y,
        "Customer Details"
    )

    y -= 20

    pdf.setFont("Helvetica", 10)

    customer_lines = [
        f"Name: {order.full_name}",
        f"Mobile: {order.mobile}",
        f"Address: {order.address}",
        f"Landmark: {order.landmark}",
        f"District: {order.district}",
        f"State: {order.state}",
        f"Pincode: {order.pincode}",
        f"Country: {order.country}",
    ]

    for line in customer_lines:
        pdf.drawString(
            50,
            y,
            line[:110]
        )
        y -= 17

    y -= 15

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(
        50,
        y,
        "Product & Payment Details"
    )

    y -= 22

    pdf.setFont("Helvetica", 10)

    lines = [
        f"Product: {order.product.title}",
        f"Product Price: Rs. {order.product_amount:.2f}",
        f"Delivery Charge: Rs. {order.delivery_charge:.2f}",
        f"Shopping Charge: Rs. {order.shopping_charge:.2f}",
        f"Total Order Value: Rs. {order.total_amount:.2f}",
        f"Payment Method: Cash on Delivery",
        f"Payment Due at Delivery: Rs. {order.cod_amount:.2f}",
        f"Payment Status: {order.get_payment_status_display()}",
        f"Order Status: {order.get_status_display()}",
    ]

    for line in lines:
        pdf.drawString(
            50,
            y,
            line[:110]
        )
        y -= 18

    y -= 20

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        50,
        y,
        "Important: Attach this invoice with the package during dispatch."
    )

    y -= 35

    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        50,
        y,
        "YN Commerce India — Thank you for your order."
    )

    y -= 15

    pdf.drawString(
        50,
        y,
        "This is a computer-generated invoice."
    )

    pdf.showPage()
    pdf.save()

    return response


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
# MY ORDERS
# ==========================

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).select_related(
        "product"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "accounts/my_orders.html",
        {
            "orders": orders
        }
    )


# ==========================
# ORDER DETAILS
# ==========================

@login_required
def order_details(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "accounts/order_details.html",
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

# =========================
# LOGOUT
# =========================
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect

def logout_view(request):
    django_logout(request)
    return redirect("home")

# ==========================
# SELLER DASHBOARD
# ==========================

@login_required
def seller_dashboard(request):
    seller = SellerProfile.objects.filter(
        user=request.user
    ).first()

    if not seller:
        return redirect("seller_register")

    if seller.status != "APPROVED":
        return redirect("seller_pending")


    if not request.user.is_staff:
        messages.error(
            request,
            "Seller access is not enabled for this account."
        )
        return redirect("home")

    from django.db.models import Count, Sum

    products = Product.objects.filter(
        owner=request.user
    )

    total_products = products.count()

    active_products = products.count()

    seller_orders = Order.objects.filter(
        product__owner=request.user
    )

    total_orders = seller_orders.count()

    delivered_orders = seller_orders.filter(
        status="DELIVERED"
    ).count()

    pending_orders = seller_orders.filter(
        status="PENDING"
    ).count()

    total_sales = seller_orders.filter(
        status="DELIVERED"
    ).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    return render(
        request,
        "accounts/seller_dashboard.html",
        {
            "user": request.user,
            "total_products": total_products,
            "active_products": active_products,
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "pending_orders": pending_orders,
            "total_sales": total_sales,
        }
    )


# ==========================
# SELLER PRODUCTS
# ==========================

@login_required
def seller_products(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Seller access is not enabled for this account."
        )
        return redirect("home")

    products = Product.objects.filter(
        owner=request.user
    ).select_related(
        "category",
        "subcategory",
        "brand",
    ).order_by("-id")

    return render(
        request,
        "accounts/seller_products.html",
        {
            "user": request.user,
            "products": products,
        }
    )


# ==========================
# SELLER REGISTRATION
# ==========================

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SellerRegistrationForm
from .models import SellerProfile


@login_required
def seller_register_view(request):

    existing_profile = SellerProfile.objects.filter(
        user=request.user
    ).first()

    if existing_profile:
        return redirect("seller_dashboard")

    if request.method == "POST":
        form = SellerRegistrationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            seller = form.save(commit=False)
            seller.user = request.user
            seller.save()

            messages.success(
                request,
                "Seller registration submitted successfully."
            )

            return redirect("seller_pending")

    else:
        form = SellerRegistrationForm(
            initial={
                "email": request.user.email,
                "mobile": request.user.phone_number,
            }
        )

    return render(
        request,
        "accounts/seller_register.html",
        {"form": form}
    )


@login_required
def seller_pending_view(request):

    profile = SellerProfile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        return redirect("seller_register")

    if profile.status == "APPROVED":
        return redirect("seller_dashboard")

    return render(
        request,
        "accounts/seller_pending.html",
        {"seller": profile}
    )


@login_required
def seller_add_product(request):
    profile = getattr(request.user, "seller_profile", None)

    if not profile or profile.status != "APPROVED":
        messages.error(request, "Seller account is not approved.")
        return redirect("seller_dashboard")

    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        price = request.POST.get("price", "").strip()
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")
        brand_id = request.POST.get("brand")
        image = request.FILES.get("image")
        images = request.FILES.getlist("images")

        if not title or not description or not price:
            messages.error(request, "Title, description and price are required.")
            return redirect("seller_add_product")

        try:
            price_value = Decimal(price)
            if price_value <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            messages.error(request, "Enter a valid product price.")
            return redirect("seller_add_product")

        product = Product(
            owner=request.user,
            title=title,
            description=description,
            price=price_value,
            image=image,
        )

        if category_id:
            product.category_id = category_id

        if subcategory_id:
            product.subcategory_id = subcategory_id

        if brand_id:
            product.brand_id = brand_id

        product.save()

        from accounts.models import ProductImage

        for index, uploaded_image in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=uploaded_image,
                sort_order=index
            )

        messages.success(request, "Product added successfully.")
        return redirect("seller_products")

    return render(
        request,
        "accounts/seller_add_product.html",
        {
            "categories": categories,
            "brands": brands,
        }
    )


@login_required
def seller_orders(request):
    profile = getattr(request.user, "seller_profile", None)

    if not profile or profile.status != "APPROVED":
        messages.error(request, "Seller account is not approved.")
        return redirect("seller_dashboard")

    orders = Order.objects.filter(
        product__owner=request.user
    ).select_related(
        "product",
        "user"
    ).order_by("-created_at")

    return render(
        request,
        "accounts/seller_orders.html",
        {
            "orders": orders,
        }
    )


@login_required
def cancel_order(request, order_id):
    from django.utils import timezone
    from django.contrib import messages
    from datetime import timedelta

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if request.method != "POST":
        return redirect("order_details", order_id=order.id)

    if order.status in ["SHIPPED", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"]:
        messages.error(request, "This order cannot be cancelled.")
        return redirect("order_details", order_id=order.id)

    now = timezone.now()
    cancellation_deadline = order.created_at + timedelta(hours=3)

    if now >= cancellation_deadline:
        messages.error(
            request,
            "Order cancellation is available only within 3 hours of placing the order."
        )
        return redirect("order_details", order_id=order.id)

    reason = request.POST.get("cancellation_reason", "").strip()

    order.status = "CANCELLED"
    order.cancelled_by_customer = True
    order.cancellation_reason = reason
    order.cancelled_at = now
    order.save(
        update_fields=[
            "status",
            "cancelled_by_customer",
            "cancellation_reason",
            "cancelled_at",
            "updated_at",
        ]
    )

    messages.success(request, "Your order has been cancelled successfully.")
    return redirect("order_details", order_id=order.id)


@login_required
def seller_accept_order(request, order_id):
    from django.utils import timezone
    from django.contrib import messages

    order = get_object_or_404(
        Order,
        id=order_id,
        product__owner=request.user
    )

    if request.method != "POST":
        return redirect("seller_orders")

    if order.status != "PENDING":
        messages.error(
            request,
            "This order cannot be accepted in its current status."
        )
        return redirect("seller_orders")

    order.status = "CONFIRMED"
    order.seller_accepted_at = timezone.now()
    order.save(
        update_fields=[
            "status",
            "seller_accepted_at",
            "updated_at",
        ]
    )

    messages.success(
        request,
        "Order accepted successfully."
    )

    return redirect("seller_orders")


@login_required
def seller_pack_order(request, order_id):
    from django.utils import timezone
    from django.contrib import messages

    order = get_object_or_404(
        Order,
        id=order_id,
        product__owner=request.user
    )

    if request.method != "POST":
        return redirect("seller_orders")

    if order.status != "CONFIRMED":
        messages.error(
            request,
            "Only confirmed orders can be marked as packed."
        )
        return redirect("seller_orders")

    order.status = "PACKED"
    order.packed_at = timezone.now()
    order.save(
        update_fields=[
            "status",
            "packed_at",
            "updated_at",
        ]
    )

    messages.success(
        request,
        "Order marked as packed successfully."
    )

    return redirect("seller_orders")


@login_required
def seller_download_label(request, order_id):
    from django.http import HttpResponse
    from django.contrib import messages

    order = get_object_or_404(
        Order,
        id=order_id,
        product__owner=request.user
    )

    if order.status not in ["PACKED", "SHIPPED", "OUT_FOR_DELIVERY", "DELIVERED"]:
        messages.error(
            request,
            "Shipping label is available after the order is packed."
        )
        return redirect("seller_orders")

    if not order.label_file:
        messages.error(
            request,
            "Shipping label has not been generated yet."
        )
        return redirect("seller_orders")

    response = HttpResponse(
        order.label_file.open("rb").read(),
        content_type="application/octet-stream"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="shipping-label-{order.id}.pdf"'
    )
    return response


@login_required
def seller_generate_label(request, order_id):
    from django.http import HttpResponse
    from django.core.files.base import ContentFile
    from django.contrib import messages
    from reportlab.pdfgen import canvas
    from io import BytesIO

    order = get_object_or_404(
        Order,
        id=order_id,
        product__owner=request.user
    )

    if request.method != "POST":
        return redirect("seller_orders")

    if order.status != "PACKED":
        messages.error(
            request,
            "Shipping label can only be generated after packing the order."
        )
        return redirect("seller_orders")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setTitle(f"Shipping Label - Order {order.id}")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, 780, "YN EXPORT INDIA")

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, 745, "SHIPPING LABEL")

    pdf.setFont("Helvetica", 10)

    y = 710
    pdf.drawString(50, y, f"Order ID: {order.id}")
    y -= 20
    pdf.drawString(50, y, f"Tracking ID: {order.tracking_id}")
    y -= 30

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "DELIVER TO")
    y -= 20

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Name: {order.full_name}")
    y -= 18
    pdf.drawString(50, y, f"Mobile: {order.mobile}")
    y -= 18
    pdf.drawString(50, y, f"Address: {order.address}")
    y -= 18
    pdf.drawString(50, y, f"Landmark: {order.landmark}")
    y -= 18
    pdf.drawString(50, y, f"District: {order.district}")
    y -= 18
    pdf.drawString(50, y, f"State: {order.state}")
    y -= 18
    pdf.drawString(50, y, f"Country: {order.country}")
    y -= 18
    pdf.drawString(50, y, f"Pincode: {order.pincode}")

    y -= 35
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "PRODUCT")

    y -= 20
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Product: {order.product.title}")
    y -= 18
    pdf.drawString(50, y, f"Amount: Rs. {order.total_amount}")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    filename = f"shipping-label-{order.id}.pdf"

    order.label_file.save(
        filename,
        ContentFile(buffer.getvalue()),
        save=False
    )
    order.save(update_fields=["label_file", "updated_at"])

    messages.success(
        request,
        "Shipping label generated successfully."
    )

    return redirect("seller_orders")


@login_required
def seller_ship_order(request, order_id):
    from django.utils import timezone
    from django.contrib import messages

    order = get_object_or_404(
        Order,
        id=order_id,
        product__owner=request.user
    )

    if request.method != "POST":
        return redirect("seller_orders")

    if order.status != "PACKED":
        messages.error(
            request,
            "Only packed orders can be marked as shipped."
        )
        return redirect("seller_orders")

    if not order.label_file:
        messages.error(
            request,
            "Generate the shipping label before shipping the order."
        )
        return redirect("seller_orders")

    order.status = "SHIPPED"
    order.shipped_at = timezone.now()
    order.save(
        update_fields=[
            "status",
            "shipped_at",
            "updated_at",
        ]
    )

    messages.success(
        request,
        "Order marked as shipped successfully."
    )

    return redirect("seller_orders")


@login_required
def seller_deliver_order(request, order_id):
    from decimal import Decimal, ROUND_DOWN
    from django.db import transaction
    from django.utils import timezone
    from django.contrib import messages

    order = get_object_or_404(
        Order,
        id=order_id,
        product__owner=request.user
    )

    if request.method != "POST":
        return redirect("seller_orders")

    if order.status not in ["SHIPPED", "OUT_FOR_DELIVERY"]:
        messages.error(
            request,
            "Only shipped orders can be marked as delivered."
        )
        return redirect("seller_orders")

    with transaction.atomic():

        # Lock the order so delivery/settlement cannot
        # accidentally be processed twice at the same time.
        order = (
            Order.objects
            .select_for_update()
            .select_related("product", "product__owner")
            .get(id=order_id)
        )

        # If already delivered, do not credit seller again.
        if order.status == "DELIVERED":
            messages.info(
                request,
                "This order has already been delivered."
            )
            return redirect("seller_orders")

        product = order.product
        seller = product.owner

        # --------------------------------------------------
        # PRODUCT PRICE
        # --------------------------------------------------
        order_amount = Decimal(
            str(product.price or "0.00")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_DOWN
        )

        # --------------------------------------------------
        # FIXED SELLER SETTLEMENT
        # Company commission = 10%
        # Seller earning = 90%
        #
        # MLM commission is separate and is NOT taken
        # from the seller's 90%.
        # --------------------------------------------------
        company_rate = Decimal("10.00")
        seller_rate = Decimal("90.00")

        company_amount = (
            order_amount * company_rate / Decimal("100.00")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_DOWN
        )

        seller_amount = (
            order_amount * seller_rate / Decimal("100.00")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_DOWN
        )

        # --------------------------------------------------
        # MARK ORDER DELIVERED
        # --------------------------------------------------
        order.status = "DELIVERED"
        order.delivered_at = timezone.now()

        order.save(
            update_fields=[
                "status",
                "delivered_at",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # SELLER SETTLEMENT
        # --------------------------------------------------
        settlement, created = (
            SellerOrderSettlement.objects
            .get_or_create(
                order=order,
                defaults={
                    "seller": seller,
                    "order_amount": order_amount,
                    "company_rate": company_rate,
                    "company_amount": company_amount,
                    "seller_rate": seller_rate,
                    "seller_amount": seller_amount,
                    "status": "SETTLED",
                    "settled_at": timezone.now(),
                },
            )
        )

        # --------------------------------------------------
        # CREDIT SELLER BALANCE ONLY ON FIRST SETTLEMENT
        # --------------------------------------------------
        if created:

            current_balance = Decimal(
                str(seller.seller_balance or "0.00")
            )

            seller.seller_balance = (
                current_balance + seller_amount
            )

            seller.save(
                update_fields=[
                    "seller_balance",
                ]
            )

    messages.success(
        request,
        (
            f"Order delivered successfully. "
            f"Seller balance credited ₹{seller_amount:.2f} "
            f"({seller_rate:.2f}% of product price)."
        )
    )

    return redirect("seller_orders")


@login_required
def bonus_balance_view(request):
    from django.shortcuts import render

    return render(
        request,
        "accounts/bonus_balance.html",
        {
            "bonus_balance": request.user.bonus_balance,
        }
    )


@login_required
def seller_products(request):
    profile = getattr(request.user, "seller_profile", None)

    if not profile or profile.status != "APPROVED":
        messages.error(request, "Seller account is not approved.")
        return redirect("seller_dashboard")

    products = Product.objects.filter(
        owner=request.user
    ).select_related(
        "category",
        "subcategory",
        "brand",
    ).order_by("-id")

    return render(
        request,
        "accounts/seller_products.html",
        {
            "user": request.user,
            "products": products,
        }
    )

@login_required
def seller_products(request):
    profile = getattr(request.user, "seller_profile", None)

    if not profile or profile.status != "APPROVED":
        messages.error(request, "Seller account is not approved.")
        return redirect("seller_dashboard")

    products = Product.objects.filter(
        owner=request.user
    ).select_related(
        "category",
        "subcategory",
        "brand",
    ).order_by("-id")

    return render(
        request,
        "accounts/seller_products.html",
        {
            "user": request.user,
            "products": products,
        }
    )

# ============================================================
# SELLER SYSTEM - FINAL AUTO APPROVAL OVERRIDE
# ============================================================

from django.contrib.auth.decorators import login_required as _seller_login_required
from django.contrib import messages as _seller_messages
from django.core.mail import send_mail as _seller_send_mail
from django.shortcuts import render as _seller_render, redirect as _seller_redirect
from django.utils import timezone as _seller_timezone
from django.db.models import Sum as _seller_Sum

from .forms import SellerRegistrationForm as _SellerRegistrationForm
from .models import SellerProfile as _SellerProfile


@_seller_login_required
def seller_register_view(request):
    """
    Seller registration.

    New seller:
        Registration -> APPROVED immediately -> Seller Dashboard

    Existing seller:
        PENDING / UNDER_REVIEW / REJECTED -> APPROVED immediately
    """

    existing_profile = _SellerProfile.objects.filter(
        user=request.user
    ).first()

    # --------------------------------------------------------
    # EXISTING SELLER
    # --------------------------------------------------------
    if existing_profile:

        if existing_profile.status != "APPROVED":
            existing_profile.status = "APPROVED"
            existing_profile.verified_at = _seller_timezone.now()
            existing_profile.rejection_reason = ""
            existing_profile.save(
                update_fields=[
                    "status",
                    "verified_at",
                    "rejection_reason",
                ]
            )

        return _seller_redirect("seller_dashboard")

    # --------------------------------------------------------
    # NEW SELLER
    # --------------------------------------------------------
    if request.method == "POST":

        form = _SellerRegistrationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            seller = form.save(commit=False)
            seller.user = request.user

            # AUTO APPROVAL
            seller.status = "APPROVED"
            seller.verified_at = _seller_timezone.now()
            seller.rejection_reason = ""

            seller.save()

            _seller_messages.success(
                request,
                "🎉 Seller registration completed successfully. "
                "Your seller account is now APPROVED."
            )

            # Email is optional. Failure must never block registration.
            try:
                if seller.email:
                    _seller_send_mail(
                        subject="YN Commerce India - Seller Account Approved",
                        message=(
                            f"Hello {seller.full_name},\n\n"
                            "Your seller registration has been completed successfully.\n\n"
                            "Seller Status: APPROVED\n\n"
                            "You can now access your Seller Dashboard.\n\n"
                            "Thank you,\n"
                            "YN Commerce India"
                        ),
                        from_email=None,
                        recipient_list=[seller.email],
                        fail_silently=True,
                    )
            except Exception:
                pass

            return _seller_redirect("seller_dashboard")

        _seller_messages.error(
            request,
            "Seller registration could not be completed. "
            "Please correct the errors shown below."
        )

    else:

        form = _SellerRegistrationForm(
            initial={
                "email": request.user.email,
                "mobile": getattr(
                    request.user,
                    "phone_number",
                    ""
                ),
                "pickup_country": "India",
            }
        )

    return _seller_render(
        request,
        "accounts/seller_register.html",
        {
            "form": form
        }
    )


@_seller_login_required
def seller_dashboard(request):

    seller = _SellerProfile.objects.filter(
        user=request.user
    ).first()

    # --------------------------------------------------------
    # NO PROFILE = SEND TO REGISTRATION
    # --------------------------------------------------------
    if not seller:
        return _seller_redirect("seller_register")

    # --------------------------------------------------------
    # ANY OLD STATUS = AUTO APPROVE
    # --------------------------------------------------------
    if seller.status != "APPROVED":
        seller.status = "APPROVED"
        seller.verified_at = _seller_timezone.now()
        seller.rejection_reason = ""
        seller.save(
            update_fields=[
                "status",
                "verified_at",
                "rejection_reason",
            ]
        )

    products = Product.objects.filter(
        owner=request.user
    )

    total_products = products.count()

    # Currently all seller products are considered active.
    active_products = products.count()

    seller_orders = Order.objects.filter(
        product__owner=request.user
    )

    total_orders = seller_orders.count()

    delivered_orders = seller_orders.filter(
        status="DELIVERED"
    ).count()

    pending_orders = seller_orders.filter(
        status="PENDING"
    ).count()

    total_sales = seller_orders.filter(
        status="DELIVERED"
    ).aggregate(
        total=_seller_Sum("total_amount")
    )["total"] or 0

    return _seller_render(
        request,
        "accounts/seller_dashboard.html",
        {
            "user": request.user,
            "seller": seller,
            "total_products": total_products,
            "active_products": active_products,
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "pending_orders": pending_orders,
            "total_sales": total_sales,
        }
    )


@_seller_login_required
def seller_products(request):

    profile = getattr(
        request.user,
        "seller_profile",
        None
    )

    if not profile:
        return _seller_redirect("seller_register")

    # AUTO APPROVE EXISTING PROFILE
    if profile.status != "APPROVED":
        profile.status = "APPROVED"
        profile.verified_at = _seller_timezone.now()
        profile.rejection_reason = ""
        profile.save(
            update_fields=[
                "status",
                "verified_at",
                "rejection_reason",
            ]
        )

    products = Product.objects.filter(
        owner=request.user
    ).select_related(
        "category",
        "subcategory",
        "brand",
    ).order_by("-id")

    return _seller_render(
        request,
        "accounts/seller_products.html",
        {
            "user": request.user,
            "seller": profile,
            "products": products,
        }
    )
