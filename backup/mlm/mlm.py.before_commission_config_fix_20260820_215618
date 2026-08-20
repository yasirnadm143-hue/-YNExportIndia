from decimal import Decimal, ROUND_DOWN

from django.db import transaction

from .models import CustomUser, CommissionTransaction
from .mlm_rank import update_user_rank


# ==========================================================
# LEVEL COMMISSION RATES
# ==========================================================

COMMISSION_RATES = {

    1: Decimal("0.04"),
    2: Decimal("0.02"),

    3: Decimal("0.01"),
    4: Decimal("0.01"),
    5: Decimal("0.01"),

    6: Decimal("0.005"),
    7: Decimal("0.005"),
    8: Decimal("0.005"),
    9: Decimal("0.005"),
    10: Decimal("0.005"),

    11: Decimal("0.0025"),
    12: Decimal("0.0025"),
    13: Decimal("0.0025"),
    14: Decimal("0.0025"),
    15: Decimal("0.0025"),
    16: Decimal("0.0025"),
    17: Decimal("0.0025"),
    18: Decimal("0.0025"),
    19: Decimal("0.0025"),
    20: Decimal("0.0025"),
}


# ==========================================================
# COMMISSION DISTRIBUTION
# ==========================================================

@transaction.atomic
def distribute_commission(order):
    """
    Commission केवल DELIVERED order पर मिलेगी.

    PENDING      -> NO COMMISSION
    CONFIRMED    -> NO COMMISSION
    PACKED       -> NO COMMISSION
    SHIPPED      -> NO COMMISSION
    OUT_FOR_DELIVERY -> NO COMMISSION
    DELIVERED    -> COMMISSION
    CANCELLED    -> NO COMMISSION

    Maximum 20 upline levels.
    """

    # ======================================================
    # DELIVERY CHECK
    # ======================================================

    if order.status != "DELIVERED":
        return []


    # ======================================================
    # ORDER USER
    # ======================================================

    source_user = order.user

    order_amount = Decimal(
        order.product.price
    )

    commissions = []

    current_user = source_user


    # ======================================================
    # 20 LEVEL LOOP
    # ======================================================

    for level in range(1, 21):

        upline_id = current_user.upline_id

        if not upline_id:
            break


        # ==================================================
        # GET UPLINE
        # ==================================================

        upline = (
            CustomUser.objects
            .select_for_update()
            .get(
                id=upline_id
            )
        )


        # ==================================================
        # UPDATE UPLINE RANK FIRST
        # ==================================================

        upline = update_user_rank(
            upline
        )


        # ==================================================
        # LEVEL RATE
        # ==================================================

        rate = COMMISSION_RATES.get(
            level,
            Decimal("0.00")
        )


        # ==================================================
        # COMMISSION AMOUNT
        # ==================================================

        amount = (
            order_amount * rate
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_DOWN
        )


        if amount <= Decimal("0.00"):

            current_user = upline

            continue


        # ==================================================
        # CREATE COMMISSION TRANSACTION
        # ==================================================

        commission, created = (
            CommissionTransaction.objects.get_or_create(

                order=order,

                beneficiary=upline,

                level=level,

                defaults={

                    "source_user": source_user,

                    "rate": rate,

                    "order_amount": order_amount,

                    "amount": amount,

                }
            )
        )


        # ==================================================
        # ADD MONEY ONLY ON FIRST CREATION
        # ==================================================

        if created:

            upline.wallet_balance += amount

            upline.save(
                update_fields=[
                    "wallet_balance"
                ]
            )

            commissions.append(
                commission
            )


        # ==================================================
        # NEXT UPLINE
        # ==================================================

        current_user = upline


    return commissions
