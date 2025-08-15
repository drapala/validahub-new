"""
Core enums used throughout the application.
"""

from enum import Enum


class ValidationStatus(str, Enum):
    """Status of a validation check"""
    PASS = "PASS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    INFO = "INFO"


class Severity(str, Enum):
    """Severity level for validation issues"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MarketplaceType(str, Enum):
    """Supported marketplace types"""
    MERCADO_LIVRE = "mercadolivre"
    SHOPEE = "shopee"
    AMAZON = "amazon"
    MAGALU = "magalu"
    AMERICANAS = "americanas"
    
    @classmethod
    def from_string(cls, value: str) -> "MarketplaceType":
        """Convert string to MarketplaceType."""
        value_lower = value.lower().replace("_", "").replace("-", "").replace(" ", "")
        mapping = {
            "mercadolivre": cls.MERCADO_LIVRE,
            "mercadolibre": cls.MERCADO_LIVRE,
            "ml": cls.MERCADO_LIVRE,
            "shopee": cls.SHOPEE,
            "amazon": cls.AMAZON,
            "amazonbr": cls.AMAZON,
            "magalu": cls.MAGALU,
            "magazineluiza": cls.MAGALU,
            "americanas": cls.AMERICANAS,
        }
        return mapping.get(value_lower, cls.MERCADO_LIVRE)