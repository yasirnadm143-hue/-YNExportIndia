from decimal import Decimal


# ==========================================================
# YN COMMERCE INDIA - MLM CONFIGURATION
# ==========================================================

# ==========================================================
# COMMISSION RATES
# ==========================================================
# Commission is calculated on PRODUCT PRICE.
# Maximum 20 upline levels.

COMMISSION_RATES = {
    1: Decimal("0.04"),       # 4%
    2: Decimal("0.02"),       # 2%

    3: Decimal("0.01"),       # 1%
    4: Decimal("0.01"),       # 1%
    5: Decimal("0.01"),       # 1%

    6: Decimal("0.005"),      # 0.5%
    7: Decimal("0.005"),
    8: Decimal("0.005"),
    9: Decimal("0.005"),
    10: Decimal("0.005"),

    11: Decimal("0.0025"),    # 0.25%
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
# RANK SYSTEM
# ==========================================================
#
# Current Level 20:
#   3 active direct downlines -> Level 30
#
# Level 30:
#   5 active direct downlines -> Level 40
#
# Level 40:
#   8 active direct downlines -> Level 50
#
# Further levels can be configured later.
#

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


# Number of ACTIVE DIRECT DOWNLINES required
# to move from the current rank to the next rank.

RANK_DOWNLINE_REQUIREMENT = {
    20: 3,
    30: 5,
    40: 8,
}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_next_rank(current_rank):
    """
    Return the next rank after current_rank.
    If there is no higher configured rank,
    return the current rank.
    """

    current_rank = int(current_rank)

    for rank in RANKS:
        if rank > current_rank:
            return rank

    return current_rank


def get_required_downlines(current_rank):
    """
    Return the number of active direct downlines
    required to reach the next rank.
    """

    return RANK_DOWNLINE_REQUIREMENT.get(
        int(current_rank),
        None,
    )


def get_commission_rate(level):
    """
    Return commission rate for an MLM level.
    """

    return COMMISSION_RATES.get(
        int(level),
        Decimal("0.00"),
    )


def get_total_commission_rate():
    """
    Return the total percentage distributed
    across all 20 levels.
    """

    return sum(
        COMMISSION_RATES.values(),
        Decimal("0.00"),
    )
