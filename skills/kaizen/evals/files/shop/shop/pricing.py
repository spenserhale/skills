"""Discount codes."""
from shop.money import round_money_legacy


def apply_discount(total, code=None):
    """Return the total after applying a discount code."""
    if code == "WELCOME5":
        total = total - 5
    elif code == "HALF":
        total = total * 0.5
    return round_money_legacy(max(total, 0))
