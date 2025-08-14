"""
Amazon Marketplace Rule Provider
"""
from typing import Dict, List
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


class AmazonRuleProvider(IRuleProvider):
    """Rule provider for Amazon marketplace"""
    
    def get_rules(self) -> Dict[str, List[IRule]]:
        """
        Returns Amazon-specific validation rules
        
        Amazon has strict requirements:
        - ASIN/SKU must follow specific format
        - Title limited to 200 chars, no promotional text
        - Bullet points required (5 max)
        - High-quality images (1000x1000 minimum)
        - EAN/UPC required for most categories
        """
        return self._get_rules_with_context({})
    
    def get_rule_by_id(self, rule_id: str) -> IRule:
        """Returns a rule by its ID"""
        rules = self.get_rules()
        for field_rules in rules.values():
            for rule in field_rules:
                if hasattr(rule, 'id') and rule.id == rule_id:
                    return rule
        return None
    
    def _get_rules_with_context(self, context: Dict[str, any]) -> Dict[str, List[IRule]]:
        """Internal method that handles context-based rule generation"""
        category = context.get('category', '').upper()
        
        # Base rules for all Amazon products
        rules = {
            'sku': [
                RequiredFieldRule(),
                RegexRule(r'^[A-Z0-9\-_]{1,40}$', 'SKU must be alphanumeric, max 40 chars'),
                MaxLengthRule(40)
            ],
            'asin': [
                RegexRule(r'^B0[A-Z0-9]{8}$', 'Invalid ASIN format (10 chars starting with B0)')
            ],
            'title': [
                RequiredFieldRule(),
                MinLengthRule(20, 'Title must be at least 20 characters'),
                MaxLengthRule(200, 'Amazon limits titles to 200 characters'),
                RegexRule(r'^[^!@#$%^&*()+=\[\]{};:\'",<>/?\\|`~]*$', 
                         'Title cannot contain special characters')
            ],
            'brand': [
                RequiredFieldRule(),
                MaxLengthRule(50, 'Brand name limited to 50 characters')
            ],
            'manufacturer': [
                RequiredFieldRule(),
                MaxLengthRule(50)
            ],
            'bullet_point_1': [
                RequiredFieldRule(),
                MinLengthRule(20, 'Bullet points must be at least 20 chars'),
                MaxLengthRule(500, 'Bullet points max 500 chars each')
            ],
            'bullet_point_2': [
                MinLengthRule(20, 'Bullet points must be at least 20 chars'),
                MaxLengthRule(500, 'Bullet points max 500 chars each')
            ],
            'bullet_point_3': [
                MinLengthRule(20, 'Bullet points must be at least 20 chars'),
                MaxLengthRule(500, 'Bullet points max 500 chars each')
            ],
            'bullet_point_4': [
                MinLengthRule(20, 'Bullet points must be at least 20 chars'),
                MaxLengthRule(500, 'Bullet points max 500 chars each')
            ],
            'bullet_point_5': [
                MinLengthRule(20, 'Bullet points must be at least 20 chars'),
                MaxLengthRule(500, 'Bullet points max 500 chars each')
            ],
            'description': [
                RequiredFieldRule(),
                MinLengthRule(100, 'Description must be at least 100 characters'),
                MaxLengthRule(2000, 'Amazon limits descriptions to 2000 characters')
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
            'main_image_url': [
                RequiredFieldRule(),
                ImageURLRule('Amazon requires valid image URLs'),
                # Amazon requires minimum 1000x1000 pixels
            ],
            'additional_image_url_1': [
                ImageURLRule('Must be valid image URL')
            ],
            'additional_image_url_2': [
                ImageURLRule('Must be valid image URL')
            ],
            'product_id': [
                RequiredFieldRule(),
                RegexRule(r'^\d{12,14}$', 'Product ID must be 12-14 digits (UPC/EAN)')
            ],
            'product_id_type': [
                RequiredFieldRule(),
                EnumRule(['UPC', 'EAN', 'ISBN', 'ASIN'], 'Invalid product ID type')
            ],
            'condition': [
                RequiredFieldRule(),
                EnumRule(['New', 'Refurbished', 'Used - Like New', 'Used - Very Good', 
                         'Used - Good', 'Used - Acceptable'], 'Invalid condition')
            ],
            'fulfillment_channel': [
                EnumRule(['FBA', 'FBM', 'DEFAULT'], 'Invalid fulfillment channel')
            ],
            'package_weight': [
                RequiredFieldRule(),
                NumericRangeRule(0.01, 1000, 'Weight in pounds (0.01-1000)')
            ],
            'package_length': [
                RequiredFieldRule(),
                NumericRangeRule(0.1, 200, 'Length in inches (0.1-200)')
            ],
            'package_width': [
                RequiredFieldRule(),
                NumericRangeRule(0.1, 200, 'Width in inches (0.1-200)')
            ],
            'package_height': [
                RequiredFieldRule(),
                NumericRangeRule(0.1, 200, 'Height in inches (0.1-200)')
            ]
        }
        
        # Category-specific rules for Amazon
        if category == 'ELETRONICOS':
            rules['model_number'] = [
                RequiredFieldRule(),
                MaxLengthRule(50)
            ]
            rules['warranty_description'] = [
                MaxLengthRule(500)
            ]
            rules['voltage'] = [
                EnumRule(['110V', '220V', '110-240V', 'USB', 'Battery Powered'], 
                        'Invalid voltage')
            ]
            rules['wattage'] = [
                NumericRangeRule(0, 10000, 'Wattage must be 0-10000')
            ]
            
        elif category == 'LIVROS':
            rules['isbn'] = [
                RequiredFieldRule(),
                RegexRule(r'^(978|979)\d{10}$', 'Invalid ISBN-13 format')
            ]
            rules['author'] = [
                RequiredFieldRule(),
                MaxLengthRule(100)
            ]
            rules['publisher'] = [
                RequiredFieldRule(),
                MaxLengthRule(100)
            ]
            rules['publication_date'] = [
                RequiredFieldRule(),
                RegexRule(r'^\d{4}-\d{2}-\d{2}$', 'Date must be YYYY-MM-DD')
            ]
            rules['pages'] = [
                RequiredFieldRule(),
                NumericRangeRule(1, 10000, 'Page count must be 1-10000')
            ]
            rules['language'] = [
                RequiredFieldRule(),
                EnumRule(['English', 'Spanish', 'Portuguese', 'French', 'German', 
                         'Italian', 'Japanese', 'Chinese'], 'Invalid language')
            ]
            
        elif category == 'MODA':
            rules['size'] = [
                RequiredFieldRule()
                # Size varies by clothing type, too complex for simple enum
            ]
            rules['color'] = [
                RequiredFieldRule(),
                MaxLengthRule(50)
            ]
            rules['material'] = [
                RequiredFieldRule(),
                MaxLengthRule(200)
            ]
            rules['care_instructions'] = [
                MaxLengthRule(500)
            ]
            rules['department'] = [
                RequiredFieldRule(),
                EnumRule(['Mens', 'Womens', 'Boys', 'Girls', 'Baby', 'Unisex'], 
                        'Invalid department')
            ]
            
        elif category == 'ALIMENTOS':
            # Amazon has very strict food requirements
            rules['expiration_date'] = [
                RequiredFieldRule(),
                RegexRule(r'^\d{4}-\d{2}-\d{2}$', 'Date must be YYYY-MM-DD')
            ]
            rules['ingredients'] = [
                RequiredFieldRule(),
                MaxLengthRule(2000, 'Ingredients list max 2000 characters')
            ]
            rules['allergen_information'] = [
                RequiredFieldRule(),
                MaxLengthRule(1000, 'Allergen info max 1000 characters')
            ]
            rules['nutritional_facts'] = [
                RequiredFieldRule(),
                MaxLengthRule(2000)
            ]
            rules['storage_instructions'] = [
                RequiredFieldRule(),
                MaxLengthRule(500)
            ]
            rules['country_of_origin'] = [
                RequiredFieldRule(),
                MaxLengthRule(100)
            ]
        
        return rules
    
    def get_column_mapping(self) -> Dict[str, str]:
        """
        Returns column name mappings for Amazon
        Maps common names to Amazon's expected format
        """
        return {
            # Common aliases to Amazon format
            'product_name': 'title',
            'product_title': 'title',
            'nome': 'title',
            'titulo': 'title',
            'name': 'title',
            
            'product_description': 'description',
            'desc': 'description',
            'descricao': 'description',
            
            'product_price': 'price',
            'preco': 'price',
            'valor': 'price',
            'list_price': 'price',
            
            'stock': 'quantity',
            'qty': 'quantity',
            'estoque': 'quantity',
            'quantidade': 'quantity',
            'inventory': 'quantity',
            
            'weight': 'package_weight',
            'peso': 'package_weight',
            
            'marca': 'brand',
            'fabricante': 'manufacturer',
            
            'foto': 'main_image_url',
            'imagem': 'main_image_url',
            'photo': 'main_image_url',
            'image': 'main_image_url',
            
            'upc': 'product_id',
            'ean': 'product_id',
            'barcode': 'product_id',
            
            'largura': 'package_width',
            'altura': 'package_height',
            'comprimento': 'package_length',
            'width': 'package_width',
            'height': 'package_height',
            'length': 'package_length',
        }
    
    def get_marketplace_name(self) -> str:
        """Returns the marketplace name"""
        return "Amazon"
    
    def get_required_columns(self) -> List[str]:
        """Returns list of required columns for Amazon"""
        return [
            'sku',
            'title',
            'brand',
            'manufacturer',
            'bullet_point_1',  # At least one bullet point required
            'description',
            'price',
            'quantity',
            'main_image_url',
            'product_id',
            'product_id_type',
            'condition',
            'package_weight',
            'package_length',
            'package_width',
            'package_height'
        ]