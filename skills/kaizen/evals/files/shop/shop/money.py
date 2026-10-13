"""Money rounding helpers."""
import warnings
from decimal import ROUND_HALF_UP, Decimal


def round_money(amount):
    """Round to cents, half up."""
    return float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def round_money_legacy(amount):
    """Deprecated alias of round_money."""
    warnings.warn(
        "round_money_legacy() is deprecated and will be removed in 2.0; use round_money()",
        DeprecationWarning,
        stacklevel=2,
    )
    return round_money(amount)
