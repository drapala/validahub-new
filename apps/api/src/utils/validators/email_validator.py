"""Email validation utilities."""


def validate_email(email: str) -> bool:
    """Simple email validation."""
    if not email:
        return False
    if "@" not in email:
        return False
    domain_part = email.split("@", 1)[1]
    if "." not in domain_part:
        return False
    return True
