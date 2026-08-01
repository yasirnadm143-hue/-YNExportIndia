from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'referral_id', 'upline', 'wallet_balance', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('MLM & Wallet Info', {'fields': ('phone_number', 'referral_id', 'upline', 'wallet_balance', 'rank')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product)
