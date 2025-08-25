"""Pricing utilities."""


def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price."""
    if price <= 0:
        raise ValueError("Price must be positive")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount
