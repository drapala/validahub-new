"""
Fixtures de respostas do MELI para testes offline.
Evita chamadas reais à API e garante testes determinísticos.
"""
from datetime import datetime, timezone
import json

# Resposta de sucesso para produto
PRODUCT_SUCCESS_RESPONSE = {
    "id": "MLB1234567890",
    "title": "Produto de Teste",
    "price": 99.99,
    "currency_id": "BRL",
    "available_quantity": 10,
    "condition": "new",
    "permalink": "https://produto.mercadolivre.com.br/...",
    "thumbnail": "https://http2.mlstatic.com/...",
    "status": "active",
    "seller_id": 123456789,
    "category_id": "MLB1234",
    "listing_type_id": "gold_pro",
    "attributes": [
        {"id": "BRAND", "name": "Marca", "value_name": "Teste"},
        {"id": "MODEL", "name": "Modelo", "value_name": "Test-001"}
    ],
    "pictures": [
        {"id": "123456-MLB", "url": "https://http2.mlstatic.com/..."},
    ],
    "shipping": {
        "mode": "me2",
        "free_shipping": True,
        "logistic_type": "fulfillment"
    }
}

# Resposta de erro 404
NOT_FOUND_RESPONSE = {
    "message": "Product not found",
    "error": "not_found",
    "status": 404,
    "cause": []
}

# Resposta de rate limit
RATE_LIMIT_RESPONSE = {
    "message": "Too many requests",
    "error": "too_many_requests",
    "status": 429,
    "cause": [],
    "headers": {
        "Retry-After": "60",
        "X-Rate-Limit-Remaining": "0",
        "X-Rate-Limit-Reset": str(int(datetime.now(timezone.utc).timestamp()) + 60)
    }
}

# Resposta de erro interno
INTERNAL_ERROR_RESPONSE = {
    "message": "Internal server error",
    "error": "internal_error",
    "status": 500,
    "cause": ["database_connection_failed"]
}

# Resposta de categoria
CATEGORY_RESPONSE = {
    "id": "MLB1234",
    "name": "Eletrônicos",
    "path_from_root": [
        {"id": "MLB1000", "name": "Eletrônicos e Tecnologia"},
        {"id": "MLB1234", "name": "Eletrônicos"}
    ],
    "attribute_types": "variations",
    "settings": {
        "listing_allowed": True,
        "price_required": True
    }
}

# Resposta de busca
SEARCH_RESPONSE = {
    "paging": {
        "total": 100,
        "offset": 0,
        "limit": 20
    },
    "results": [
        PRODUCT_SUCCESS_RESPONSE,
        {
            "id": "MLB9876543210",
            "title": "Outro Produto",
            "price": 199.99,
            "currency_id": "BRL",
            "available_quantity": 5,
            "condition": "new",
            "status": "active"
        }
    ],
    "filters": [],
    "available_filters": []
}

# Resposta de usuário/vendedor
USER_RESPONSE = {
    "id": 123456789,
    "nickname": "TESTESELLER",
    "registration_date": "2020-01-01T10:00:00.000-03:00",
    "country_id": "BR",
    "user_type": "normal",
    "logo": None,
    "points": 100,
    "site_id": "MLB",
    "permalink": "http://perfil.mercadolivre.com.br/TESTESELLER",
    "seller_reputation": {
        "level_id": "5_green",
        "power_seller_status": "platinum",
        "transactions": {
            "total": 1000,
            "completed": 950,
            "canceled": 50,
            "ratings": {
                "positive": 0.95,
                "negative": 0.03,
                "neutral": 0.02
            }
        }
    }
}

# Resposta de ordem
ORDER_RESPONSE = {
    "id": 2000000000,
    "date_created": "2024-01-01T10:00:00.000-03:00",
    "date_closed": "2024-01-01T11:00:00.000-03:00",
    "last_updated": "2024-01-01T11:00:00.000-03:00",
    "status": "paid",
    "status_detail": None,
    "order_items": [
        {
            "item": {
                "id": "MLB1234567890",
                "title": "Produto de Teste",
                "variation_id": None
            },
            "quantity": 2,
            "unit_price": 99.99,
            "currency_id": "BRL"
        }
    ],
    "total_amount": 199.98,
    "currency_id": "BRL",
    "buyer": {
        "id": 987654321,
        "nickname": "TESTBUYER"
    },
    "seller": {
        "id": 123456789,
        "nickname": "TESTESELLER"
    }
}

# Resposta com timeout simulado (para testes de resiliência)
TIMEOUT_RESPONSE = {
    "_simulate": "timeout",
    "_delay_seconds": 35
}

def get_mock_response(endpoint_type, status="success"):
    """
    Retorna uma resposta mock baseada no tipo de endpoint e status.
    
    Args:
        endpoint_type: product, category, search, user, order
        status: success, not_found, rate_limit, error, timeout
    """
    responses = {
        "product": {
            "success": PRODUCT_SUCCESS_RESPONSE,
            "not_found": NOT_FOUND_RESPONSE,
            "rate_limit": RATE_LIMIT_RESPONSE,
            "error": INTERNAL_ERROR_RESPONSE,
            "timeout": TIMEOUT_RESPONSE
        },
        "category": {
            "success": CATEGORY_RESPONSE,
            "not_found": NOT_FOUND_RESPONSE,
            "error": INTERNAL_ERROR_RESPONSE
        },
        "search": {
            "success": SEARCH_RESPONSE,
            "error": INTERNAL_ERROR_RESPONSE,
            "rate_limit": RATE_LIMIT_RESPONSE
        },
        "user": {
            "success": USER_RESPONSE,
            "not_found": NOT_FOUND_RESPONSE,
            "error": INTERNAL_ERROR_RESPONSE
        },
        "order": {
            "success": ORDER_RESPONSE,
            "not_found": NOT_FOUND_RESPONSE,
            "error": INTERNAL_ERROR_RESPONSE
        }
    }
    
    return responses.get(endpoint_type, {}).get(status, INTERNAL_ERROR_RESPONSE)

def generate_batch_responses(endpoint_type, count=10, success_rate=0.9):
    """
    Gera uma lista de respostas para simular batch processing.
    
    Args:
        endpoint_type: Tipo de endpoint
        count: Número de respostas
        success_rate: Taxa de sucesso (0.0 a 1.0)
    """
    import random
    responses = []
    
    for i in range(count):
        if random.random() < success_rate:
            response = get_mock_response(endpoint_type, "success")
            # Variar o ID para cada resposta
            if "id" in response:
                response = response.copy()
                response["id"] = f"{response['id'][:3]}{1000000000 + i}"
        else:
            # Distribuir erros aleatoriamente
            error_types = ["not_found", "rate_limit", "error"]
            response = get_mock_response(endpoint_type, random.choice(error_types))
            
        responses.append(response)
    
    return responses