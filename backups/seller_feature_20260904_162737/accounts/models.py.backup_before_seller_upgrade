import random
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    referral_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    upline = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="downlines"
    )

    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rank = models.CharField(max_length=50, default="Member")

    # MLM numeric rank
    mlm_level = models.PositiveSmallIntegerField(
        default=20
    )

    # Number of unique active downlines that
    # have contributed toward the next rank.
    active_downline_count = models.PositiveIntegerField(
        default=0
    )

    def save(self, *args, **kwargs):
        if not self.referral_id:
            self.referral_id = "YN" + "".join(
                random.choices("0123456789", k=6)
            )
        super().save(*args, **kwargs)




# ==========================
# PRODUCT CATALOG
# ==========================

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    icon = models.ImageField(
        upload_to="category_icons/",
        blank=True,
        null=True
    )
    banner = models.ImageField(
        upload_to="category_banners/",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"],
                name="unique_subcategory_category_slug"
            )
        ]

    def __str__(self):
        return f"{self.category.name} / {self.name}"


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    logo = models.ImageField(
        upload_to="brand_logos/",
        blank=True,
        null=True
    )
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )


    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to="product_images/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title


class Order(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Order Pending"),
        ("CONFIRMED", "Order Confirmed"),
        ("PACKED", "Order Packed"),
        ("SHIPPED", "Order Shipped"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)

    mobile = models.CharField(max_length=15)
    pincode = models.CharField(max_length=10)

    landmark = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    address = models.TextField()

    # Order tracking
    tracking_id = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    # ==========================
    # PAYMENT & ORDER CHARGES
    # ==========================

    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=85.00
    )

    shopping_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=15.00
    )

    product_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    online_payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    cod_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Payment Pending"),
        ("AWAITING_VERIFICATION", "Awaiting Verification"),
        ("VERIFIED", "Payment Verified"),
        ("REJECTED", "Payment Rejected"),
    ]

    payment_status = models.CharField(
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )

    payment_screenshot = models.ImageField(
        upload_to="payment_screenshots/",
        blank=True,
        null=True
    )

    payment_verified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.tracking_id:
            self.tracking_id = (
                "YNTRK"
                + "".join(
                    random.choices(
                        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                        k=10
                    )
                )
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class CommissionTransaction(models.Model):

    LEVEL_RATES = {
        1: 0.04,
        2: 0.02,
        3: 0.01,
        4: 0.01,
        5: 0.01,
        6: 0.005,
        7: 0.005,
        8: 0.005,
        9: 0.005,
        10: 0.005,
        11: 0.0025,
        12: 0.0025,
        13: 0.0025,
        14: 0.0025,
        15: 0.0025,
        16: 0.0025,
        17: 0.0025,
        18: 0.0025,
        19: 0.0025,
        20: 0.0025,
    }

    beneficiary = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="commission_transactions"
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="commission_transactions"
    )

    source_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="generated_commissions"
    )

    level = models.PositiveSmallIntegerField()

    rate = models.DecimalField(
        max_digits=7,
        decimal_places=5
    )

    order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["level", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "beneficiary", "level"],
                name="unique_order_beneficiary_level_commission"
            )
        ]

    def __str__(self):
        return (
            f"Level {self.level} - "
            f"{self.beneficiary.username} - "
            f"₹{self.amount}"
        )


class Notification(models.Model):

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.title} - {self.user.username}"


# ==========================
# CUSTOMER SUPPORT SYSTEM
# ==========================

class SupportTicket(models.Model):

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("NORMAL", "Normal"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    ]

    ticket_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="support_tickets"
    )

    email = models.EmailField()

    subject = models.CharField(
        max_length=200
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="NORMAL"
    )

    admin_reply = models.TextField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.ticket_id:
            self.ticket_id = (
                "YNCS"
                + uuid.uuid4().hex[:10].upper()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"


class SupportMessage(models.Model):

    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_messages"
    )

    message = models.TextField()

    is_staff_reply = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.ticket.ticket_id} - Support Message"
