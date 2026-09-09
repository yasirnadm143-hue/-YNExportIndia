from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Product, Order


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "phone_number",
        "referral_id",
        "wallet_balance",
        "rank",
        "is_staff",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "MLM & Wallet",
            {
                "fields": (
                    "phone_number",
                    "referral_id",
                    "upline",
                    "wallet_balance",
                    "rank",
                )
            },
        ),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price")
    search_fields = ("title",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "product",
        "mobile",
        "state",
        "created_at",
    )

    search_fields = (
        "full_name",
        "mobile",
        "pincode",
    )

    list_filter = (
        "state",
        "country",
        "created_at",
    )
