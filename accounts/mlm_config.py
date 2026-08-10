from decimal import Decimal


# ==========================================================
# RANK COMMISSION POOL
# ==========================================================

RANK_COMMISSION_POOL = {
    20: Decimal("0.20"),
    30: Decimal("0.25"),
    40: Decimal("0.28"),
    50: Decimal("0.32"),
    60: Decimal("0.35"),
    70: Decimal("0.40"),
    80: Decimal("0.43"),
    90: Decimal("0.46"),
}


# ==========================================================
# NEW ACTIVE DOWNLINES REQUIRED FOR NEXT RANK
# ==========================================================

RANK_DOWNLINE_REQUIREMENT = {
    20: 3,
    30: 5,
    40: 8,

    # 50, 60, 70, 80 को अभी
    # तुम्हारे final rules मिलने के बाद भरेंगे।
}


# ==========================================================
# RANK ORDER
# ==========================================================

RANKS = [
    20,
    30,
    40,
    50,
    60,
    70,
    80,
    90,
]


def get_next_rank(current_rank):
    """
    Return next MLM rank.
    """

    current_rank = int(current_rank)

    for rank in RANKS:

        if rank > current_rank:
            return rank

    return 90


def get_required_downlines(current_rank):
    """
    Return number of NEW active downlines
    required for next rank.
    """

    return RANK_DOWNLINE_REQUIREMENT.get(
        int(current_rank)
    )


def get_commission_pool_rate(rank):
    """
    Return maximum commission pool percentage
    for a given rank.
    """

    return RANK_COMMISSION_POOL.get(
        int(rank),
        Decimal("0.00")
    )
