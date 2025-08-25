"""
Mercado Livre (MELI) specific models.
These models represent the raw format from MELI API.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MeliRuleAttribute(BaseModel):
    """MELI attribute rule definition."""
    id: str
    name: str
    value_type: str  # STRING, NUMBER, BOOLEAN, etc.
    value_max_length: Optional[int] = None
    value_min_length: Optional[int] = None
    value_pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    required: bool = False
    tags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class MeliCategory(BaseModel):
    """MELI category definition."""
    id: str
    name: str
    picture: Optional[str] = None
    permalink: Optional[str] = None
    total_items_in_this_category: Optional[int] = None
    path_from_root: Optional[List[Dict[str, str]]] = None
    children_categories: Optional[List[Dict[str, Any]]] = None
    attributes: Optional[List[MeliRuleAttribute]] = None
    settings: Optional[Dict[str, Any]] = None
    meta_categ_id: Optional[str] = None
    attribute_types: Optional[str] = None


class MeliListingType(BaseModel):
    """MELI listing type definition."""
    id: str
    name: str
    site_id: str
    configuration: Optional[Dict[str, Any]] = None


class MeliCondition(BaseModel):
    """MELI item condition."""
    id: str
    name: str
    value_struct: Optional[Dict[str, Any]] = None


class MeliShipping(BaseModel):
    """MELI shipping configuration."""
    mode: str
    free_shipping: bool = False
    tags: Optional[List[str]] = None
    dimensions: Optional[str] = None
    local_pick_up: bool = False
    methods: Optional[List[Dict[str, Any]]] = None
    costs: Optional[List[Dict[str, Any]]] = None


class MeliItemValidationRule(BaseModel):
    """MELI item validation rule."""
    attribute_id: str
    attribute_name: str
    validation_type: str  # REQUIRED, MIN_LENGTH, MAX_LENGTH, PATTERN, etc.
    validation_value: Optional[Any] = None
    error_message: Optional[str] = None
    severity: str = "ERROR"  # ERROR, WARNING, INFO


class MeliRuleSet(BaseModel):
    """Complete MELI rule set for a category."""
    category_id: str
    site_id: str = "MLB"  # Default to Brazil
    category: Optional[MeliCategory] = None
    required_attributes: List[MeliRuleAttribute] = Field(default_factory=list)
    optional_attributes: List[MeliRuleAttribute] = Field(default_factory=list)
    validation_rules: List[MeliItemValidationRule] = Field(default_factory=list)
    listing_types: List[MeliListingType] = Field(default_factory=list)
    conditions: List[MeliCondition] = Field(default_factory=list)
    shipping_options: Optional[MeliShipping] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MeliApiError(BaseModel):
    """MELI API error response."""
    message: str
    error: str
    status: int
    cause: Optional[List[Dict[str, Any]]] = None
    
    
class MeliApiResponse(BaseModel):
    """Generic MELI API response wrapper."""
    status: int
    data: Optional[Any] = None
    error: Optional[MeliApiError] = None
    headers: Optional[Dict[str, str]] = None
