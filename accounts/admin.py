from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'mobile_number', 'upline_id', 'is_staff', 'date_joined')
    search_fields = ('username', 'mobile_number', 'upline_id', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('MLM & Extra Info', {'fields': ('mobile_number', 'upline_id', 'pan_card', 'aadhaar_card')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
