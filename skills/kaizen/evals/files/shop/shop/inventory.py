"""Stock reservation."""


def reserve(stock, quantity):
    """Reserve quantity from stock and return what is left.

    Reserving more than is in stock clamps the remainder at zero.
    """
    return max(stock - quantity, 0)
