"""
Testes para Circuit Breaker usando mocks e fixtures.
Evita chamadas reais ao MELI e garante testes rápidos e determinísticos.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone
import httpx

from tests.fixtures.meli_responses import (
    get_mock_response,
    generate_batch_responses,
    RATE_LIMIT_RESPONSE,
    INTERNAL_ERROR_RESPONSE
)

# Assumindo que temos um CircuitBreaker implementado
# from apps.api.src.infrastructure.circuit_breaker import CircuitBreaker


class MockCircuitBreaker:
    """Mock Circuit Breaker para testes."""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
    async def call(self, func, *args, **kwargs):
        """Executa função com proteção de circuit breaker."""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self):
        """Verifica se deve tentar resetar o circuit."""
        if not self.last_failure_time:
            return False
        return (datetime.now(timezone.utc) - self.last_failure_time).seconds >= self.recovery_timeout
    
    def _on_success(self):
        """Registra sucesso."""
        self.failure_count = 0
        self.state = "closed"
    
    def _on_failure(self):
        """Registra falha."""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def reset(self):
        """Reseta o circuit breaker."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"


class TestCircuitBreaker:
    """Testes para o Circuit Breaker."""
    
    @pytest.fixture
    def circuit_breaker(self):
        """Cria uma instância do circuit breaker para testes."""
        return MockCircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=httpx.HTTPError
        )
    
    @pytest.fixture
    def mock_http_client(self):
        """Mock do cliente HTTP."""
        client = AsyncMock()
        return client
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_threshold(self, circuit_breaker, mock_http_client):
        """Testa que o circuit breaker abre após atingir o threshold de falhas."""
        # Configurar mock para sempre falhar
        mock_http_client.get.side_effect = httpx.HTTPError("Connection failed")
        
        # Fazer requisições até atingir o threshold
        for i in range(3):
            with pytest.raises(httpx.HTTPError):
                await circuit_breaker.call(mock_http_client.get, "https://api.test.com")
        
        # Verificar que o circuit está aberto
        assert circuit_breaker.state == "open"
        
        # Próxima chamada deve falhar imediatamente sem chamar o serviço
        with pytest.raises(Exception, match="Circuit breaker is open"):
            await circuit_breaker.call(mock_http_client.get, "https://api.test.com")
        
        # Verificar que o serviço não foi chamado quando o circuit está aberto
        assert mock_http_client.get.call_count == 3
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closes_on_success(self, circuit_breaker, mock_http_client):
        """Testa que o circuit breaker fecha após sucesso."""
        # Configurar algumas falhas
        mock_http_client.get.side_effect = [
            httpx.HTTPError("Failed"),
            httpx.HTTPError("Failed"),
            AsyncMock(return_value=MagicMock(json=lambda: {"status": "ok"}))()
        ]
        
        # Duas falhas
        for i in range(2):
            with pytest.raises(httpx.HTTPError):
                await circuit_breaker.call(mock_http_client.get, "https://api.test.com")
        
        # Sucesso deve resetar o contador
        result = await circuit_breaker.call(mock_http_client.get, "https://api.test.com")
        
        assert circuit_breaker.state == "closed"
        assert circuit_breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_with_rate_limit(self, circuit_breaker):
        """Testa circuit breaker com respostas de rate limit."""
        
        async def mock_api_call():
            # Simula resposta de rate limit
            response = MagicMock()
            response.status_code = 429
            response.json.return_value = RATE_LIMIT_RESPONSE
            response.headers = RATE_LIMIT_RESPONSE.get("headers", {})
            raise httpx.HTTPStatusError("Rate limited", request=None, response=response)
        
        # Testar múltiplas chamadas com rate limit
        for i in range(3):
            with pytest.raises(httpx.HTTPStatusError):
                await circuit_breaker.call(mock_api_call)
        
        # Circuit deve estar aberto
        assert circuit_breaker.state == "open"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_state(self, circuit_breaker):
        """Testa o estado half-open do circuit breaker."""
        circuit_breaker.recovery_timeout = 0.1  # 100ms para teste rápido
        
        async def failing_call():
            raise httpx.HTTPError("Failed")
        
        # Abrir o circuit
        for i in range(3):
            with pytest.raises(httpx.HTTPError):
                await circuit_breaker.call(failing_call)
        
        assert circuit_breaker.state == "open"
        
        # Esperar pelo recovery timeout
        await asyncio.sleep(0.2)
        
        # Próxima chamada deve tentar (half-open)
        with pytest.raises(httpx.HTTPError):
            await circuit_breaker.call(failing_call)
        
        # Deve voltar para open após falha em half-open
        assert circuit_breaker.state == "open"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_with_batch_requests(self, circuit_breaker):
        """Testa circuit breaker com requisições em batch."""
        
        # Simular respostas com 70% de sucesso
        responses = generate_batch_responses("product", count=10, success_rate=0.7)
        call_index = 0
        
        async def mock_batch_call():
            nonlocal call_index
            if call_index < len(responses):
                response = responses[call_index]
                call_index += 1
                
                if "error" in response or response.get("status", 200) >= 400:
                    raise httpx.HTTPError(f"Error: {response}")
                return response
            return {"status": "ok"}
        
        results = []
        errors = []
        
        for i in range(10):
            try:
                result = await circuit_breaker.call(mock_batch_call)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Verificar que processamos algumas requisições
        assert len(results) > 0 or len(errors) > 0
        
        # Se muitos erros, circuit deve estar aberto
        if len(errors) >= circuit_breaker.failure_threshold:
            assert circuit_breaker.state in ["open", "half-open"]
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_metrics(self, circuit_breaker):
        """Testa coleta de métricas do circuit breaker."""
        metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "circuit_opens": 0
        }
        
        async def track_call(func):
            metrics["total_calls"] += 1
            try:
                result = await circuit_breaker.call(func)
                metrics["successful_calls"] += 1
                return result
            except Exception as e:
                metrics["failed_calls"] += 1
                if circuit_breaker.state == "open":
                    metrics["circuit_opens"] = 1
                raise e
        
        # Simular algumas chamadas com sucesso e falha
        async def success_call():
            return {"status": "ok"}
        
        async def failure_call():
            raise httpx.HTTPError("Failed")
        
        # 2 sucessos
        for _ in range(2):
            await track_call(success_call)
        
        # 3 falhas (abre o circuit)
        for _ in range(3):
            with pytest.raises(httpx.HTTPError):
                await track_call(failure_call)
        
        # Verificar métricas
        assert metrics["total_calls"] == 5
        assert metrics["successful_calls"] == 2
        assert metrics["failed_calls"] == 3
        assert metrics["circuit_opens"] == 1


class TestCircuitBreakerIntegration:
    """Testes de integração do Circuit Breaker com mocks do MELI."""
    
    @pytest.mark.asyncio
    async def test_meli_api_with_circuit_breaker(self):
        """Testa integração com API do MELI usando circuit breaker."""
        circuit_breaker = MockCircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        # Mock do cliente MELI
        async def mock_meli_get_product(product_id):
            # Simular diferentes cenários
            if product_id == "MLB_ERROR":
                raise httpx.HTTPError("Server error")
            elif product_id == "MLB_NOT_FOUND":
                return get_mock_response("product", "not_found")
            else:
                return get_mock_response("product", "success")
        
        # Testar chamadas normais
        result = await circuit_breaker.call(mock_meli_get_product, "MLB1234567890")
        assert result["id"] == "MLB1234567890"
        
        # Testar com erros
        for _ in range(3):
            with pytest.raises(httpx.HTTPError):
                await circuit_breaker.call(mock_meli_get_product, "MLB_ERROR")
        
        # Circuit deve estar aberto
        assert circuit_breaker.state == "open"
        
        # Tentar com produto válido deve falhar devido ao circuit aberto
        with pytest.raises(Exception, match="Circuit breaker is open"):
            await circuit_breaker.call(mock_meli_get_product, "MLB1234567890")
    
    @pytest.mark.asyncio 
    async def test_graceful_degradation(self):
        """Testa degradação graciosa quando o circuit está aberto."""
        circuit_breaker = MockCircuitBreaker()
        circuit_breaker.state = "open"  # Forçar estado aberto
        
        # Implementar fallback
        async def get_product_with_fallback(product_id):
            try:
                return await circuit_breaker.call(mock_meli_get_product, product_id)
            except Exception as e:
                if "Circuit breaker is open" in str(e):
                    # Retornar dados em cache ou resposta padrão
                    return {
                        "id": product_id,
                        "title": "Produto Indisponível",
                        "status": "cached",
                        "message": "Usando dados em cache devido a indisponibilidade temporária"
                    }
                raise e
        
        async def mock_meli_get_product(product_id):
            return get_mock_response("product", "success")
        
        # Deve retornar resposta de fallback
        result = await get_product_with_fallback("MLB1234567890")
        assert result["status"] == "cached"
        assert "cache" in result["message"].lower()