"""
Simple validators for demonstration of mutation testing.
"""


def validate_positive_number(value: float) -> bool:
    """Check if a number is positive."""
    return value > 0


def validate_email(email: str) -> bool:
    """Simple email validation."""
    if not email:
        return False
    if "@" not in email:
        return False
    if "." not in email.split("@")[1]:
        return False
    return True


def validate_product_id(product_id: str) -> bool:
    """Validate product ID format."""
    if not product_id:
        return False
    if len(product_id) < 6:
        return False
    if not product_id.startswith("ML"):
        return False
    return True


def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price."""
    if price <= 0:
        raise ValueError("Price must be positive")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount