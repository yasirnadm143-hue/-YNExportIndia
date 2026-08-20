from django.db import transaction

from .models import CustomUser


# ==========================================================
# RANK REQUIREMENTS
# ==========================================================

RANK_REQUIREMENTS = {
    20: 3,   # Level 20 -> Level 30 : 3 active direct downlines
    30: 5,   # Level 30 -> Level 40 : 5 active direct downlines
    40: 8,   # Level 40 -> Level 50 : 8 active direct downlines

    # बाद में final rules के अनुसार:
    # 50: ...,
    # 60: ...,
    # 70: ...,
    # 80: ...,
}


RANK_SEQUENCE = [
    20,
    30,
    40,
    50,
    60,
    70,
    80,
    90,
]


# ==========================================================
# NEXT RANK
# ==========================================================

def get_next_rank(current_rank):

    current_rank = int(current_rank)

    for rank in RANK_SEQUENCE:

        if rank > current_rank:
            return rank

    return current_rank


# ==========================================================
# ACTIVE DIRECT DOWNLINES
# ==========================================================

def get_active_direct_downline_count(user):
    """
    केवल direct downlines count होंगे।

    Downline को active मानने के लिए
    उसका कम से कम एक order DELIVERED होना जरूरी है.

    केवल registration करने से active नहीं होगी.
    CONFIRMED/PENDING order भी active नहीं मानी जाएगी.
    """

    from .models import Order

    direct_downlines = CustomUser.objects.filter(
        upline=user
    )

    count = 0

    for member in direct_downlines:

        delivered_order = Order.objects.filter(
            user=member,
            status="DELIVERED"
        ).exists()

        if delivered_order:
            count += 1

    return count


# ==========================================================
# UPDATE USER RANK
# ==========================================================

@transaction.atomic
def update_user_rank(user):

    user = CustomUser.objects.select_for_update().get(
        pk=user.pk
    )

    active_count = get_active_direct_downline_count(
        user
    )

    current_rank = int(user.mlm_level)

    # ======================================================
    # RANK PROGRESSION
    # ======================================================

    while True:

        next_rank = get_next_rank(
            current_rank
        )

        if next_rank == current_rank:
            break

        required = RANK_REQUIREMENTS.get(
            current_rank
        )

        if required is None:
            break

        if active_count < required:
            break

        current_rank = next_rank

    # ======================================================
    # SAVE
    # ======================================================

    user.active_downline_count = active_count
    user.mlm_level = current_rank
    user.rank = f"Level {current_rank}"

    user.save(
        update_fields=[
            "active_downline_count",
            "mlm_level",
            "rank",
        ]
    )

    return user
