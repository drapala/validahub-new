"""
Shopee Marketplace Rule Provider
"""
from typing import Dict, List, Optional
from src.core.interfaces import IRuleProvider, IRule
from src.rules.base import (
    RequiredFieldRule,
    MaxLengthRule,
    MinLengthRule,
    RegexRule,
    URLRule,
    NumericRangeRule,
    EnumRule,
    ImageURLRule,
)


class ShopeeRuleProvider(IRuleProvider):
    """Rule provider for Shopee marketplace"""
    
    def get_rules(self) -> Dict[str, List[IRule]]:
        """
        Returns Shopee-specific validation rules
        
        Shopee has specific requirements:
        - SKU must be unique and alphanumeric
        - Title limited to 100 chars with emoji support
        - Price in local currency with 2 decimal places
        - Images must be square (1:1 ratio preferred)
        - Categories from Shopee's taxonomy
        """
        return self._get_rules_with_context({})
    
    def get_rule_by_id(self, rule_id: str) -> Optional[IRule]:
        """Returns a rule by its ID"""
        rules = self.get_rules()
        for field_rules in rules.values():
            for rule in field_rules:
                if getattr(rule, 'rule_id', None) == rule_id:
                    return rule
        return None
    
    def _get_rules_with_context(self, context: Dict[str, any]) -> Dict[str, List[IRule]]:
        """Internal method that handles context-based rule generation"""
        category = context.get('category', '').upper()
        
        # Base rules for all Shopee products
        rules = {
            'sku': [
                RequiredFieldRule(),
                RegexRule(r'^[A-Z0-9\-_]+$', 'SKU must be alphanumeric with hyphens/underscores only'),
                MaxLengthRule(50)
            ],
            'title': [
                RequiredFieldRule(),
                MinLengthRule(10, 'Title must be at least 10 characters'),
                MaxLengthRule(100, 'Shopee limits titles to 100 characters')
            ],
            'description': [
                RequiredFieldRule(),
                MinLengthRule(50, 'Description must be at least 50 characters'),
                MaxLengthRule(3000, 'Shopee limits descriptions to 3000 characters')
            ],
            'price': [
                RequiredFieldRule(),
                NumericRangeRule(0.01, 999999.99, 'Price must be between 0.01 and 999999.99'),
                RegexRule(r'^\d+\.\d{2}$', 'Price must have exactly 2 decimal places')
            ],
            'quantity': [
                RequiredFieldRule(),
                NumericRangeRule(0, 99999, 'Quantity must be between 0 and 99999')
            ],
            'weight': [
                RequiredFieldRule(),
                NumericRangeRule(1, 300000, 'Weight in grams (1g to 300kg)')
            ],
            'brand': [
                MaxLengthRule(50, 'Brand name limited to 50 characters')
            ],
            'image_url': [
                RequiredFieldRule(),
                ImageURLRule('Shopee requires valid image URLs'),
                # Note: Shopee prefers 1:1 ratio images, but this would require image processing
            ],
            'category_id': [
                RequiredFieldRule(),
                RegexRule(r'^\d+$', 'Category ID must be numeric')
            ],
            'condition': [
                RequiredFieldRule(),
                EnumRule(['new', 'used', 'refurbished'], 'Condition must be: new, used, or refurbished')
            ],
            'package_width': [
                NumericRangeRule(1, 200, 'Width in cm (1-200)')
            ],
            'package_height': [
                NumericRangeRule(1, 200, 'Height in cm (1-200)')
            ],
            'package_length': [
                NumericRangeRule(1, 200, 'Length in cm (1-200)')
            ]
        }
        
        # Category-specific rules for Shopee
        if category == 'ELETRONICOS':
            rules['warranty'] = [
                RequiredFieldRule(),
                EnumRule(['no_warranty', '1_month', '3_months', '6_months', '1_year', '2_years'], 
                        'Invalid warranty period')
            ]
            rules['model'] = [
                RequiredFieldRule(),
                MaxLengthRule(100)
            ]
            rules['voltage'] = [
                EnumRule(['110V', '220V', 'Bivolt', 'USB', 'Battery'], 'Invalid voltage')
            ]
            
        elif category == 'MODA':
            rules['size'] = [
                RequiredFieldRule(),
                EnumRule(['PP', 'P', 'M', 'G', 'GG', 'XG', 'XXG', 'XXXG'], 'Invalid size')
            ]
            rules['color'] = [
                RequiredFieldRule(),
                MaxLengthRule(30)
            ]
            rules['material'] = [
                RequiredFieldRule(),
                MaxLengthRule(100)
            ]
            rules['gender'] = [
                RequiredFieldRule(),
                EnumRule(['male', 'female', 'unisex', 'kids'], 'Invalid gender')
            ]
            
        elif category == 'BELEZA':
            rules['expiry_date'] = [
                RequiredFieldRule(),
                RegexRule(r'^\d{4}-\d{2}-\d{2}$', 'Date must be in YYYY-MM-DD format')
            ]
            rules['volume'] = [
                MaxLengthRule(20, 'Volume description max 20 chars (e.g., "100ml", "50g")')
            ]
            rules['skin_type'] = [
                EnumRule(['all', 'dry', 'oily', 'combination', 'sensitive'], 'Invalid skin type')
            ]
            
        elif category == 'ALIMENTOS':
            rules['expiry_date'] = [
                RequiredFieldRule(),
                RegexRule(r'^\d{4}-\d{2}-\d{2}$', 'Date must be in YYYY-MM-DD format')
            ]
            rules['ingredients'] = [
                RequiredFieldRule(),
                MaxLengthRule(1000, 'Ingredients list max 1000 characters')
            ]
            rules['allergens'] = [
                MaxLengthRule(500, 'Allergen info max 500 characters')
            ]
            rules['storage'] = [
                RequiredFieldRule(),
                EnumRule(['room_temp', 'refrigerated', 'frozen'], 'Invalid storage type')
            ]
        
        return rules
    
    def get_column_mapping(self) -> Dict[str, str]:
        """
        Returns column name mappings for Shopee
        Maps common names to Shopee's expected format
        """
        return {
            # Common aliases to Shopee format
            'product_name': 'title',
            'product_title': 'title',
            'nome': 'title',
            'titulo': 'title',
            
            'product_description': 'description',
            'desc': 'description',
            'descricao': 'description',
            
            'product_price': 'price',
            'preco': 'price',
            'valor': 'price',
            
            'stock': 'quantity',
            'qty': 'quantity',
            'estoque': 'quantity',
            'quantidade': 'quantity',
            
            'product_weight': 'weight',
            'peso': 'weight',
            
            'marca': 'brand',
            
            'foto': 'image_url',
            'imagem': 'image_url',
            'photo': 'image_url',
            
            'categoria': 'category_id',
            'category': 'category_id',
            
            'condicao': 'condition',
            'estado': 'condition',
            
            'largura': 'package_width',
            'altura': 'package_height',
            'comprimento': 'package_length',
        }
    
    def get_marketplace_name(self) -> str:
        """Returns the marketplace name"""
        return "Shopee"
    
    def get_required_columns(self) -> List[str]:
        """Returns list of required columns for Shopee"""
        return [
            'sku',
            'title', 
            'description',
            'price',
            'quantity',
            'weight',
            'image_url',
            'category_id',
            'condition'
        ]