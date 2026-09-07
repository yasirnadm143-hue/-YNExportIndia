from django.db import transaction

from .models import CustomUser, Order
from .mlm_config import (
    RANKS,
    get_next_rank,
    get_required_downlines,
)


# ==========================================================
# ACTIVE DIRECT DOWNLINES
# ==========================================================

def get_active_direct_downline_count(user):
    """
    A direct downline is considered ACTIVE only when
    that user has at least one DELIVERED order.

    PENDING / CONFIRMED / PACKED / SHIPPED /
    OUT_FOR_DELIVERY orders do not make a user active.
    """

    direct_downlines = CustomUser.objects.filter(
        upline=user
    )

    count = 0

    for member in direct_downlines:

        has_delivered_order = Order.objects.filter(
            user=member,
            status="DELIVERED",
        ).exists()

        if has_delivered_order:
            count += 1

    return count


# ==========================================================
# UPDATE USER RANK
# ==========================================================

@transaction.atomic
def update_user_rank(user):
    """
    Recalculate the user's MLM rank.

    Rank can move upward when the required number of
    active direct downlines is reached.

    Rank never moves downward.
    """

    user = CustomUser.objects.select_for_update().get(
        pk=user.pk
    )

    current_rank = int(user.mlm_level or RANKS[0])

    active_count = get_active_direct_downline_count(
        user
    )

    # ======================================================
    # RANK PROGRESSION
    # ======================================================

    while True:

        next_rank = get_next_rank(
            current_rank
        )

        # Already at the highest configured rank.
        if next_rank == current_rank:
            break

        required = get_required_downlines(
            current_rank
        )

        # No rule configured for this rank.
        if required is None:
            break

        # Not enough active direct downlines yet.
        if active_count < required:
            break

        # Requirement fulfilled.
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
