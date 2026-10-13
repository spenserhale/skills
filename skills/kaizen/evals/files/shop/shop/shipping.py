"""Shipping cost."""
from shop.money import round_money_legacy

FREE_SHIPPING_THRESHOLD = 75


def shipping_cost(subtotal, weight_kg):
    """Flat rate plus a per-kilogram charge; free at or above the threshold."""
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return 0.0
    return round_money_legacy(4.99 + 1.25 * weight_kg)
