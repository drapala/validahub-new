"""Product ID validation utilities."""


def validate_product_id(product_id: str) -> bool:
    """Validate product ID format."""
    if not product_id:
        return False
    if len(product_id) < 6:
        return False
    if not product_id.startswith("ML"):
        return False
    return True
