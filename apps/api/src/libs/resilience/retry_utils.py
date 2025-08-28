"""
Utilitários de retry e resiliência.
Implementa backoff exponencial com jitter e respeita Retry-After.
"""
import asyncio
import random
import time
from datetime import datetime, timezone
from typing import Optional, Callable, Any, TypeVar, Union
from functools import wraps
import httpx
from email.utils import parsedate_to_datetime

T = TypeVar('T')

class RetryError(Exception):
    """Erro quando todas as tentativas de retry falham."""
    pass

class RetryConfig:
    """Configuração para retry com backoff exponencial."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter_min: float = 0.5,  # 50% do delay
        jitter_max: float = 1.5,  # 150% do delay
        respect_retry_after: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter_min = jitter_min
        self.jitter_max = jitter_max
        self.respect_retry_after = respect_retry_after
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calcula delay com backoff exponencial e jitter.
        """
        # Backoff exponencial
        delay = self.initial_delay * (self.exponential_base ** attempt)
        
        # Limitar ao máximo
        delay = min(delay, self.max_delay)
        
        # Aplicar jitter para evitar thundering herd
        jitter_factor = random.uniform(self.jitter_min, self.jitter_max)
        delay = delay * jitter_factor
        
        return delay

def parse_retry_after(headers: dict) -> Optional[float]:
    """
    Parse do header Retry-After (segundos ou HTTP-date).
    """
    retry_after = headers.get("Retry-After", headers.get("retry-after"))
    if not retry_after:
        return None
    
    # Tentar parse como inteiro (segundos)
    try:
        return float(retry_after)
    except ValueError:
        pass
    
    # Tentar parse como HTTP-date
    try:
        retry_date = parsedate_to_datetime(retry_after)
        if retry_date:
            now = datetime.now(timezone.utc)
            delta = (retry_date - now).total_seconds()
            return max(0, delta)
    except Exception:
        pass
    
    return None

async def retry_async(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,),
    **kwargs
) -> T:
    """
    Executa função assíncrona com retry e backoff exponencial.
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        
        except exceptions as e:
            last_exception = e
            
            # Se for a última tentativa, não fazer retry
            if attempt >= config.max_attempts - 1:
                break
            
            # Calcular delay
            delay = config.calculate_delay(attempt)
            
            # Verificar Retry-After em respostas HTTP
            if config.respect_retry_after and isinstance(e, httpx.HTTPStatusError):
                response = e.response
                if response and response.status_code in (429, 503):
                    retry_after = parse_retry_after(dict(response.headers))
                    if retry_after is not None:
                        delay = retry_after
            
            # Aguardar antes do próximo retry
            await asyncio.sleep(delay)
    
    # Todas as tentativas falharam
    raise RetryError(f"Failed after {config.max_attempts} attempts") from last_exception

def retry_sync(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,),
    **kwargs
) -> T:
    """
    Executa função síncrona com retry e backoff exponencial.
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            return func(*args, **kwargs)
        
        except exceptions as e:
            last_exception = e
            
            # Se for a última tentativa, não fazer retry
            if attempt >= config.max_attempts - 1:
                break
            
            # Calcular delay
            delay = config.calculate_delay(attempt)
            
            # Verificar Retry-After em respostas HTTP
            if config.respect_retry_after and hasattr(e, 'response'):
                response = getattr(e, 'response', None)
                if response and hasattr(response, 'status_code'):
                    if response.status_code in (429, 503):
                        headers = getattr(response, 'headers', {})
                        retry_after = parse_retry_after(dict(headers))
                        if retry_after is not None:
                            delay = retry_after
            
            # Aguardar antes do próximo retry
            time.sleep(delay)
    
    # Todas as tentativas falharam
    raise RetryError(f"Failed after {config.max_attempts} attempts") from last_exception

def with_retry(
    max_attempts: int = 3,
    exceptions: tuple = (Exception,),
    initial_delay: float = 1.0,
    max_delay: float = 60.0
):
    """
    Decorator para adicionar retry a funções.
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay
    )
    
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await retry_async(
                    func, *args,
                    config=config,
                    exceptions=exceptions,
                    **kwargs
                )
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return retry_sync(
                    func, *args,
                    config=config,
                    exceptions=exceptions,
                    **kwargs
                )
            return sync_wrapper
    
    return decorator

class ExponentialBackoff:
    """
    Classe para gerenciar backoff exponencial com estado.
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.attempt = 0
        self.last_retry = None
    
    def reset(self):
        """Reseta o contador de tentativas."""
        self.attempt = 0
        self.last_retry = None
    
    def next_delay(self) -> float:
        """Calcula o próximo delay."""
        delay = self.config.calculate_delay(self.attempt)
        self.attempt += 1
        self.last_retry = time.monotonic()
        return delay
    
    def should_retry(self) -> bool:
        """Verifica se deve fazer retry."""
        return self.attempt < self.config.max_attempts
    
    async def wait(self) -> None:
        """Aguarda o próximo retry (async)."""
        if self.should_retry():
            delay = self.next_delay()
            await asyncio.sleep(delay)
        else:
            raise RetryError(f"Max attempts ({self.config.max_attempts}) exceeded")
    
    def wait_sync(self) -> None:
        """Aguarda o próximo retry (sync)."""
        if self.should_retry():
            delay = self.next_delay()
            time.sleep(delay)
        else:
            raise RetryError(f"Max attempts ({self.config.max_attempts}) exceeded")

async def retry_with_circuit_breaker(
    func: Callable[..., T],
    *args,
    circuit_breaker: Any,
    retry_config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """
    Combina retry com circuit breaker para máxima resiliência.
    """
    config = retry_config or RetryConfig()
    
    async def wrapped_func():
        return await circuit_breaker.call(func, *args, **kwargs)
    
    return await retry_async(
        wrapped_func,
        config=config,
        exceptions=(Exception,)
    )

class AdaptiveRetry:
    """
    Retry adaptativo que ajusta delays baseado em taxa de sucesso.
    """
    
    def __init__(self, base_config: Optional[RetryConfig] = None):
        self.base_config = base_config or RetryConfig()
        self.success_count = 0
        self.failure_count = 0
        self.current_multiplier = 1.0
    
    def record_success(self):
        """Registra sucesso e ajusta multiplier."""
        self.success_count += 1
        # Reduzir delay se muitos sucessos
        if self.success_count > 10:
            self.current_multiplier = max(0.5, self.current_multiplier * 0.9)
    
    def record_failure(self):
        """Registra falha e ajusta multiplier."""
        self.failure_count += 1
        # Aumentar delay se muitas falhas
        if self.failure_count > 3:
            self.current_multiplier = min(3.0, self.current_multiplier * 1.2)
    
    def get_config(self) -> RetryConfig:
        """Retorna configuração ajustada."""
        config = RetryConfig(
            max_attempts=self.base_config.max_attempts,
            initial_delay=self.base_config.initial_delay * self.current_multiplier,
            max_delay=self.base_config.max_delay,
            exponential_base=self.base_config.exponential_base,
            jitter_min=self.base_config.jitter_min,
            jitter_max=self.base_config.jitter_max,
            respect_retry_after=self.base_config.respect_retry_after
        )
        return config
    
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Executa com retry adaptativo."""
        try:
            result = await retry_async(
                func, *args,
                config=self.get_config(),
                **kwargs
            )
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e