from django.contrib.auth.models import AbstractUser
from django.db import models
import random


class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    pan_card = models.CharField(max_length=20, blank=True, null=True)
    aadhaar_card = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    upline = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="downlines"
    )

    referral_id = models.CharField(max_length=20, unique=True, blank=True)
    referral_link = models.URLField(blank=True, null=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.referral_id:
            while True:
                code = "YN" + str(random.randint(1000000000, 9999999999))
                if not CustomUser.objects.filter(referral_id=code).exists():
                    self.referral_id = code
                    self.referral_link = f"https://ynexportindia.onrender.com/register/?ref={code}"
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="product_images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Order(models.Model):

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Packed", "Packed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    full_name = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    tracking_id = models.CharField(max_length=20, unique=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    ordered_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            while True:
                code = "YN" + str(random.randint(1000000000, 9999999999))
                if not Order.objects.filter(tracking_id=code).exists():
                    self.tracking_id = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_id
class SupportTicket(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class Notification(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class Wallet(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"{self.user.username} Wallet"


class ReferralIncome(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="referral_income"
    )

    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="generated_income"
    )

    level = models.PositiveIntegerField()

    commission_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Level {self.level}"


class RechargeRequest(models.Model):

    STATUS = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    screenshot = models.ImageField(
        upload_to="recharge/"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount}"

