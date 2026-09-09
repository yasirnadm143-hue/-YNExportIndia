from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .models import CustomUser, Product, Order, SupportTicket, SupportMessage, SellerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "phone_number",
        "referral_id",
        "bonus_balance",
        "rank",
        "is_staff",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "MLM & Bonus Balance",
            {
                "fields": (
                    "phone_number",
                    "referral_id",
                    "upline",
                    "bonus_balance",
                    "rank",
                )
            },
        ),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "price",
    )

    search_fields = (
        "title",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "full_name",
        "product",
        "online_payment_amount",
        "cod_amount",
        "payment_status",
        "status",
        "created_at",
    )

    search_fields = (
        "full_name",
        "mobile",
        "pincode",
        "tracking_id",
        "user__username",
    )

    list_filter = (
        "payment_status",
        "status",
        "state",
        "country",
        "created_at",
    )

    readonly_fields = (
        "tracking_id",
        "product_amount",
        "delivery_charge",
        "shopping_charge",
        "total_amount",
        "online_payment_amount",
        "cod_amount",
        "payment_verified_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "product",
                    "user",
                    "tracking_id",
                    "status",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Customer / Delivery",
            {
                "fields": (
                    "full_name",
                    "first_name",
                    "last_name",
                    "father_name",
                    "mobile",
                    "pincode",
                    "landmark",
                    "district",
                    "state",
                    "country",
                    "address",
                )
            },
        ),
        (
            "Payment Calculation",
            {
                "fields": (
                    "product_amount",
                    "delivery_charge",
                    "shopping_charge",
                    "total_amount",
                    "online_payment_amount",
                    "cod_amount",
                )
            },
        ),
        (
            "Payment Verification",
            {
                "fields": (
                    "payment_status",
                    "payment_screenshot",
                    "payment_verified_at",
                )
            },
        ),
    )

    actions = (
        "verify_selected_payments",
        "reject_selected_payments",
        "mark_selected_packed",
        "mark_selected_shipped",
        "mark_selected_out_for_delivery",
        "mark_selected_delivered",
    )

    @admin.action(description="✅ Verify selected payments")
    def verify_selected_payments(self, request, queryset):

        updated = 0

        for order in queryset:

            if order.payment_status == "VERIFIED":
                continue

            order.payment_status = "VERIFIED"
            order.payment_verified_at = timezone.now()
            order.status = "CONFIRMED"

            order.save(
                update_fields=[
                    "payment_status",
                    "payment_verified_at",
                    "status",
                    "updated_at",
                ]
            )

            updated += 1

        self.message_user(
            request,
            f"{updated} payment(s) verified and order(s) confirmed."
        )

    @admin.action(description="📦 Mark selected orders as Packed")
    def mark_selected_packed(self, request, queryset):
        updated = queryset.filter(
            payment_status="VERIFIED",
            status="CONFIRMED",
        ).update(status="PACKED")

        self.message_user(
            request,
            f"{updated} order(s) marked as Packed."
        )

    @admin.action(description="🚚 Mark selected orders as Shipped")
    def mark_selected_shipped(self, request, queryset):
        updated = queryset.filter(
            payment_status="VERIFIED",
            status="PACKED",
        ).update(status="SHIPPED")

        self.message_user(
            request,
            f"{updated} order(s) marked as Shipped."
        )

    @admin.action(description="🚛 Mark selected orders as Out for Delivery")
    def mark_selected_out_for_delivery(self, request, queryset):
        updated = queryset.filter(
            payment_status="VERIFIED",
            status="SHIPPED",
        ).update(status="OUT_FOR_DELIVERY")

        self.message_user(
            request,
            f"{updated} order(s) marked as Out for Delivery."
        )

    @admin.action(description="✅ Mark selected orders as Delivered")
    def mark_selected_delivered(self, request, queryset):
        updated = queryset.filter(
            payment_status="VERIFIED",
            status="OUT_FOR_DELIVERY",
        ).update(status="DELIVERED")

        self.message_user(
            request,
            f"{updated} order(s) marked as Delivered. MLM commission will be processed automatically."
        )

    @admin.action(description="❌ Reject selected payments")
    def reject_selected_payments(self, request, queryset):

        updated = 0

        for order in queryset:

            if order.payment_status == "VERIFIED":
                continue

            order.payment_status = "REJECTED"

            order.save(
                update_fields=[
                    "payment_status",
                    "updated_at",
                ]
            )

            updated += 1

        self.message_user(
            request,
            f"{updated} payment(s) rejected."
        )

# ==========================
# CUSTOMER SUPPORT ADMIN
# ==========================

class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    fields = (
        "sender",
        "message",
        "is_staff_reply",
        "created_at",
    )
    readonly_fields = (
        "created_at",
    )


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):

    list_display = (
        "ticket_id",
        "user",
        "subject",
        "status",
        "priority",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "ticket_id",
        "subject",
        "email",
        "user__username",
        "user__email",
    )

    list_filter = (
        "status",
        "priority",
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "ticket_id",
        "user",
        "email",
        "subject",
        "message",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "🎫 Ticket Information",
            {
                "fields": (
                    "ticket_id",
                    "user",
                    "email",
                    "subject",
                    "message",
                )
            },
        ),
        (
            "⚙️ Ticket Management",
            {
                "fields": (
                    "status",
                    "priority",
                    "admin_reply",
                )
            },
        ),
        (
            "🕒 Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    inlines = (
        SupportMessageInline,
    )

    def save_model(self, request, obj, form, change):
        old_reply = ""

        if change:
            old_obj = SupportTicket.objects.get(pk=obj.pk)
            old_reply = (old_obj.admin_reply or "").strip()

        new_reply = (obj.admin_reply or "").strip()

        super().save_model(request, obj, form, change)

        # Create a conversation message only when Admin
        # has entered a new reply.
        if new_reply and new_reply != old_reply:
            SupportMessage.objects.create(
                ticket=obj,
                sender=request.user,
                message=new_reply,
                is_staff_reply=True,
            )

            # Automatically move the ticket to In Progress
            # when staff sends a reply, unless already resolved/closed.
            if obj.status not in ["RESOLVED", "CLOSED"]:
                obj.status = "IN_PROGRESS"
                obj.save(update_fields=["status", "updated_at"])


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):

    list_display = (
        "ticket",
        "sender",
        "is_staff_reply",
        "created_at",
    )

    search_fields = (
        "ticket__ticket_id",
        "ticket__subject",
        "sender__username",
        "message",
    )

    list_filter = (
        "is_staff_reply",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )


# ==========================================================
# SELLER KYC / REGISTRATION ADMIN
# ==========================================================

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "full_name",
        "email",
        "mobile",
        "status",
        "created_at",
        "verified_at",
    )

    list_filter = (
        "status",
        "created_at",
        "verified_at",
    )

    search_fields = (
        "full_name",
        "email",
        "mobile",
        "pan_number",
        "aadhaar_number",
        "user__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "verified_at",
    )

    fieldsets = (
        (
            "Seller Account",
            {
                "fields": (
                    "user",
                    "full_name",
                    "email",
                    "mobile",
                    "age",
                )
            },
        ),
        (
            "KYC Verification",
            {
                "fields": (
                    "pan_number",
                    "pan_card",
                    "aadhaar_number",
                    "aadhaar_card",
                )
            },
        ),
        (
            "Bank Details",
            {
                "fields": (
                    "bank_account_name",
                    "bank_account_number",
                    "ifsc_code",
                )
            },
        ),
        (
            "Pickup Address",
            {
                "fields": (
                    "pickup_address",
                    "pickup_pincode",
                    "pickup_district",
                    "pickup_state",
                    "pickup_country",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": (
                    "status",
                    "rejection_reason",
                    "verified_at",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    actions = (
        "approve_selected_sellers",
        "reject_selected_sellers",
        "mark_under_review",
    )

    @admin.action(description="✅ Approve selected sellers")
    def approve_selected_sellers(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(
            status="APPROVED",
            verified_at=timezone.now(),
            rejection_reason="",
        )

        self.message_user(
            request,
            f"{updated} seller(s) approved successfully."
        )

    @admin.action(description="🔎 Mark selected sellers Under Review")
    def mark_under_review(self, request, queryset):
        updated = queryset.update(
            status="UNDER_REVIEW"
        )

        self.message_user(
            request,
            f"{updated} seller(s) moved to Under Review."
        )

    @admin.action(description="❌ Reject selected sellers")
    def reject_selected_sellers(self, request, queryset):
        updated = queryset.update(
            status="REJECTED"
        )

        self.message_user(
            request,
            f"{updated} seller(s) rejected."
        )
