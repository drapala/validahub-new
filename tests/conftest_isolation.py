"""
Configurações para garantir isolamento de unit tests.
Unit tests não devem depender de recursos externos como banco de dados.
"""
import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Generator, Any
import asyncio

# Marcar testes que precisam de banco de dados
pytest.mark.requires_db = pytest.mark.skipif(
    os.getenv("SKIP_DB_TESTS", "false").lower() == "true",
    reason="Skipping database tests"
)

# Fixture para detectar e prevenir conexões reais em unit tests
@pytest.fixture(autouse=True, scope="function")
def prevent_db_access(request):
    """
    Previne acesso ao banco de dados em unit tests.
    Testes marcados com @pytest.mark.integration podem acessar o banco.
    """
    if "integration" in request.keywords or "requires_db" in request.keywords:
        # Testes de integração podem acessar o banco
        yield
        return
    
    # Para unit tests, fazer mock de todas as conexões de banco
    with patch("asyncpg.connect") as mock_connect, \
         patch("sqlalchemy.create_engine") as mock_engine, \
         patch("sqlalchemy.ext.asyncio.create_async_engine") as mock_async_engine, \
         patch("psycopg2.connect") as mock_psycopg2:
        
        # Configurar mocks para falhar se chamados
        error_msg = "Unit tests should not access the database. Use mocks or mark test with @pytest.mark.integration"
        
        mock_connect.side_effect = AssertionError(error_msg)
        mock_engine.side_effect = AssertionError(error_msg)
        mock_async_engine.side_effect = AssertionError(error_msg)
        mock_psycopg2.side_effect = AssertionError(error_msg)
        
        yield

# Mock de sessão de banco de dados para unit tests
@pytest.fixture
def mock_db_session():
    """
    Fornece uma sessão de banco mockada para unit tests.
    """
    session = MagicMock()
    session.query = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    session.flush = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    
    # Configurar query builder
    query = session.query.return_value
    query.filter = MagicMock(return_value=query)
    query.filter_by = MagicMock(return_value=query)
    query.first = MagicMock(return_value=None)
    query.all = MagicMock(return_value=[])
    query.one = MagicMock(side_effect=Exception("No results found"))
    query.one_or_none = MagicMock(return_value=None)
    query.count = MagicMock(return_value=0)
    query.order_by = MagicMock(return_value=query)
    query.limit = MagicMock(return_value=query)
    query.offset = MagicMock(return_value=query)
    
    return session

# Mock assíncrono de sessão
@pytest.fixture
def mock_async_db_session():
    """
    Fornece uma sessão assíncrona de banco mockada.
    """
    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = MagicMock()
    
    return session

# Mock de repositório genérico
@pytest.fixture
def mock_repository():
    """
    Fornece um repositório mockado genérico.
    """
    repo = MagicMock()
    repo.get = AsyncMock(return_value=None)
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_all = AsyncMock(return_value=[])
    repo.create = AsyncMock(return_value=MagicMock(id=1))
    repo.update = AsyncMock(return_value=MagicMock(id=1))
    repo.delete = AsyncMock(return_value=True)
    repo.exists = AsyncMock(return_value=False)
    repo.count = AsyncMock(return_value=0)
    
    return repo

# Fixture para isolar testes de Redis
@pytest.fixture(autouse=True, scope="function")
def prevent_redis_access(request):
    """
    Previne acesso ao Redis em unit tests.
    """
    if "integration" in request.keywords or "requires_redis" in request.keywords:
        yield
        return
    
    with patch("redis.Redis") as mock_redis, \
         patch("redis.asyncio.Redis") as mock_async_redis, \
         patch("aioredis.create_redis_pool") as mock_aioredis:
        
        error_msg = "Unit tests should not access Redis. Use mocks or mark test with @pytest.mark.integration"
        
        mock_redis.side_effect = AssertionError(error_msg)
        mock_async_redis.side_effect = AssertionError(error_msg)
        mock_aioredis.side_effect = AssertionError(error_msg)
        
        yield

# Mock de cliente Redis
@pytest.fixture
def mock_redis_client():
    """
    Fornece um cliente Redis mockado.
    """
    client = MagicMock()
    client.get = MagicMock(return_value=None)
    client.set = MagicMock(return_value=True)
    client.delete = MagicMock(return_value=1)
    client.exists = MagicMock(return_value=0)
    client.expire = MagicMock(return_value=True)
    client.ttl = MagicMock(return_value=-2)
    client.incr = MagicMock(return_value=1)
    client.decr = MagicMock(return_value=0)
    client.hget = MagicMock(return_value=None)
    client.hset = MagicMock(return_value=1)
    client.hdel = MagicMock(return_value=1)
    client.hgetall = MagicMock(return_value={})
    
    return client

# Fixture para isolar testes de APIs externas
@pytest.fixture(autouse=True, scope="function")
def prevent_external_api_access(request):
    """
    Previne chamadas a APIs externas em unit tests.
    """
    if "integration" in request.keywords or "external_api" in request.keywords:
        yield
        return
    
    import httpx
    import requests
    import aiohttp
    
    with patch.object(httpx, "get") as mock_httpx_get, \
         patch.object(httpx, "post") as mock_httpx_post, \
         patch.object(httpx.AsyncClient, "get") as mock_async_get, \
         patch.object(httpx.AsyncClient, "post") as mock_async_post, \
         patch.object(requests, "get") as mock_requests_get, \
         patch.object(requests, "post") as mock_requests_post:
        
        error_msg = "Unit tests should not call external APIs. Use mocks or mark test with @pytest.mark.integration"
        
        mock_httpx_get.side_effect = AssertionError(error_msg)
        mock_httpx_post.side_effect = AssertionError(error_msg)
        mock_async_get.side_effect = AssertionError(error_msg)
        mock_async_post.side_effect = AssertionError(error_msg)
        mock_requests_get.side_effect = AssertionError(error_msg)
        mock_requests_post.side_effect = AssertionError(error_msg)
        
        yield

# Mock de cliente HTTP
@pytest.fixture
def mock_http_client():
    """
    Fornece um cliente HTTP mockado.
    """
    client = AsyncMock()
    response = MagicMock()
    response.status_code = 200
    response.json = MagicMock(return_value={})
    response.text = "OK"
    response.headers = {}
    
    client.get = AsyncMock(return_value=response)
    client.post = AsyncMock(return_value=response)
    client.put = AsyncMock(return_value=response)
    client.delete = AsyncMock(return_value=response)
    client.patch = AsyncMock(return_value=response)
    
    return client

# Fixture para isolar testes de sistema de arquivos
@pytest.fixture
def temp_directory(tmp_path):
    """
    Fornece um diretório temporário isolado para testes.
    """
    return tmp_path

# Configuração para testes assíncronos
@pytest.fixture
def event_loop():
    """
    Cria um event loop para testes assíncronos.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Marcadores customizados para categorizar testes
def pytest_configure(config):
    """
    Registra marcadores customizados.
    """
    config.addinivalue_line(
        "markers", "unit: marca testes como unit tests (isolados)"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes que precisam de recursos externos"
    )
    config.addinivalue_line(
        "markers", "requires_db: marca testes que precisam de banco de dados"
    )
    config.addinivalue_line(
        "markers", "requires_redis: marca testes que precisam de Redis"
    )
    config.addinivalue_line(
        "markers", "external_api: marca testes que chamam APIs externas"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes lentos que podem ser pulados em CI"
    )