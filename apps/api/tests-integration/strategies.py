"""
Estratégias customizadas do Hypothesis para ValidaHub.
Limitações bem definidas para evitar falsos positivos e flaky tests.
"""
from hypothesis import strategies as st
from datetime import datetime, timezone
import string

# Estratégias para tipos básicos com limites sensatos
def valid_email():
    """Email válido com limites razoáveis."""
    local = st.text(
        alphabet=string.ascii_letters + string.digits + "._-",
        min_size=1,
        max_size=64
    )
    domain = st.text(
        alphabet=string.ascii_lowercase + string.digits + ".-",
        min_size=4,
        max_size=255
    ).filter(lambda x: "." in x and not x.startswith(".") and not x.endswith("."))
    
    return st.builds(lambda l, d: f"{l}@{d}", local, domain)

def valid_url():
    """URL válida com protocolo HTTP/HTTPS."""
    protocol = st.sampled_from(["http", "https"])
    domain = st.text(
        alphabet=string.ascii_lowercase + string.digits + ".-",
        min_size=4,
        max_size=100
    ).filter(lambda x: "." in x and not x.startswith(".") and not x.endswith("."))
    path = st.text(
        alphabet=string.ascii_letters + string.digits + "/-_",
        max_size=200
    )
    
    return st.builds(lambda p, d, pt: f"{p}://{d}/{pt}", protocol, domain, path)

def marketplace_id():
    """IDs de marketplace válidos do MELI."""
    return st.sampled_from([
        "MLB", "MLA", "MLM", "MLC", "MLU", "MCO", "MPE", "MLV"
    ])

def currency_code():
    """Códigos de moeda válidos."""
    return st.sampled_from([
        "BRL", "ARS", "MXN", "CLP", "UYU", "COP", "PEN", "VES", "USD"
    ])

def price_amount():
    """Valores de preço realistas (0.01 a 1000000.00)."""
    return st.decimals(
        min_value=0.01,
        max_value=1000000.00,
        places=2
    )

def product_id():
    """IDs de produto no formato MELI."""
    prefix = marketplace_id()
    numbers = st.integers(min_value=100000000, max_value=999999999)
    return st.builds(lambda p, n: f"{p}{n}", prefix, numbers)

def datetime_utc():
    """Datetime com timezone UTC."""
    return st.datetimes(
        min_value=datetime(2020, 1, 1, tzinfo=timezone.utc),
        max_value=datetime(2030, 12, 31, tzinfo=timezone.utc),
        timezones=st.just(timezone.utc)
    )

def safe_string(min_size=0, max_size=100):
    """String segura sem caracteres problemáticos."""
    return st.text(
        alphabet=string.ascii_letters + string.digits + " .-_",
        min_size=min_size,
        max_size=max_size
    ).filter(lambda x: x.strip() if min_size > 0 else True)

def batch_size():
    """Tamanhos de batch realistas."""
    return st.integers(min_value=1, max_value=100)

def retry_count():
    """Número de retries sensato."""
    return st.integers(min_value=0, max_value=10)

def timeout_seconds():
    """Timeouts em segundos (1s a 5min)."""
    return st.integers(min_value=1, max_value=300)

def port_number():
    """Números de porta válidos."""
    return st.integers(min_value=1024, max_value=65535)

def percentage():
    """Porcentagem (0 a 100)."""
    return st.floats(min_value=0.0, max_value=100.0)

def json_safe_dict():
    """Dicionário que pode ser serializado em JSON."""
    return st.dictionaries(
        keys=safe_string(min_size=1, max_size=50),
        values=st.one_of(
            st.none(),
            st.booleans(),
            st.integers(min_value=-1000000, max_value=1000000),
            st.floats(min_value=-1000000.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
            safe_string(max_size=1000)
        ),
        max_size=20
    )