from typing import Dict, Type

from src.schemas.validate import Marketplace
from src.core.interfaces import IRuleProvider

from src.rules.marketplaces.mercado_livre.provider import MercadoLivreRuleProvider
from src.rules.marketplaces.shopee.provider import ShopeeRuleProvider
from src.rules.marketplaces.amazon.provider import AmazonRuleProvider

# Mapping between marketplaces and their corresponding rule provider classes
MARKETPLACE_PROVIDERS: Dict[Marketplace, Type[IRuleProvider]] = {
    Marketplace.MERCADO_LIVRE: MercadoLivreRuleProvider,
    Marketplace.SHOPEE: ShopeeRuleProvider,
    Marketplace.AMAZON: AmazonRuleProvider,
}
