"""
HTTP client for Mercado Livre API.
Handles authentication, rate limiting, and API communication.
"""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
import asyncio
from functools import wraps
import time
import random

from src.core.logging_config import get_logger
from ..models.meli_models import (
    MeliCategory,
    MeliRuleAttribute,
    MeliApiError,
    MeliApiResponse,
    MeliListingType,
    MeliCondition
)

logger = get_logger(__name__)


class RateLimiter:
    """Thread-safe rate limiter for API calls."""
    
    def __init__(self, calls_per_second: float = 10):
        if calls_per_second <= 0:
            raise ValueError(f"calls_per_second must be positive, got {calls_per_second}")
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
        self._lock = asyncio.Lock()
    
    async def wait(self):
        """Wait if necessary to respect rate limit (thread-safe)."""
        async with self._lock:
            current = time.monotonic()  # Use monotonic clock to avoid drift
            elapsed = current - self.last_call
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self.last_call = time.monotonic()


def with_retry(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator for retrying failed API calls."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        base_wait = backoff_factor ** attempt
                        # Add jitter: randomize between 50% and 150% of base wait time
                        jitter = random.uniform(0.5, 1.5)
                        wait_time = base_wait * jitter
                        logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time:.2f}s: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"API call failed after {max_retries} attempts: {e}")
            raise last_exception
        return wrapper
    return decorator


class MeliClient:
    """
    HTTP client for Mercado Livre API.
    
    This client handles:
    - Authentication with MELI API
    - Rate limiting to avoid API throttling
    - Retry logic for transient failures
    - Response parsing and error handling
    """
    
    BASE_URL = "https://api.mercadolibre.com"
    AUTH_URL = "https://api.mercadolibre.com/oauth/token"
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        site_id: str = "MLB",  # Default to Brazil
        rate_limit: float = 10  # Calls per second
    ):
        """
        Initialize MELI client.
        
        Args:
            client_id: OAuth client ID (optional if using access_token)
            client_secret: OAuth client secret (optional if using access_token)
            access_token: Pre-obtained access token (optional)
            site_id: MELI site ID (MLB for Brazil, MLA for Argentina, etc.)
            rate_limit: Maximum API calls per second
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.site_id = site_id
        self.rate_limiter = RateLimiter(rate_limit)
        self._client: Optional[httpx.AsyncClient] = None
        self._token_expires_at: Optional[datetime] = None
        self._context_count = 0
        self._context_lock = asyncio.Lock()
    
    async def __aenter__(self):
        """Async context manager entry (reentrant for concurrent use)."""
        async with self._context_lock:
            if self._context_count == 0:
                # Create client only on first entry
                self._client = httpx.AsyncClient(
                    base_url=self.BASE_URL,
                    timeout=httpx.Timeout(30.0),
                    headers={
                        "User-Agent": "ValidaHub/1.0",
                        "Accept": "application/json"
                    }
                )
            self._context_count += 1
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit (reentrant for concurrent use)."""
        async with self._context_lock:
            self._context_count -= 1
            if self._context_count == 0 and self._client:
                # Close only when last context exits
                await self._client.aclose()
                self._client = None
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token."""
        if self.access_token and self._token_expires_at:
            if datetime.now(timezone.utc) < self._token_expires_at:
                return
        
        if self.client_id and self.client_secret:
            await self._refresh_token()
        elif not self.access_token:
            raise ValueError("No authentication method available. Provide either access_token or client_id/client_secret")
    
    async def _refresh_token(self):
        """Refresh OAuth access token."""
        if not self.client_id or not self.client_secret:
            raise ValueError("Cannot refresh token without client_id and client_secret")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.AUTH_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            response.raise_for_status()
            
            # Safely parse JSON response
            try:
                data = response.json()
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to parse OAuth token response: {e}")
                raise ValueError(f"Invalid OAuth response format: {e}")
            
            if "access_token" not in data:
                raise ValueError("OAuth response missing access_token field")
            
            self.access_token = data["access_token"]
            expires_in = data.get("expires_in", 21600)  # Default 6 hours
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            
            logger.info(f"OAuth token refreshed, expires at {self._token_expires_at}")
    
    @with_retry(max_retries=3)
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        authenticated: bool = False
    ) -> MeliApiResponse:
        """
        Make HTTP request to MELI API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body for POST/PUT requests
            authenticated: Whether to include auth header
            
        Returns:
            MeliApiResponse with status, data, and error info
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        # Ensure authentication if needed
        if authenticated:
            await self._ensure_authenticated()
        
        # Apply rate limiting
        await self.rate_limiter.wait()
        
        # Prepare headers
        headers = {}
        if authenticated and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        # Make request
        try:
            response = await self._client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
                headers=headers
            )
            
            # Parse response
            if response.status_code >= 400:
                # Safely parse JSON error response
                try:
                    error_data = response.json() if response.content else {}
                except (ValueError, TypeError):
                    error_data = {"message": response.text or "Unknown error"}
                
                # Raise exception for retry logic to work
                # Retry on server errors (5xx) and rate limiting (429)
                if response.status_code >= 500 or response.status_code == 429:
                    response.raise_for_status()
                # For other 4xx errors, return error response without retrying
                return MeliApiResponse(
                    status=response.status_code,
                    error=MeliApiError(
                        message=error_data.get("message", "Unknown error"),
                        error=error_data.get("error", ""),
                        status=response.status_code,
                        cause=error_data.get("cause")
                    ),
                    headers=dict(response.headers)
                )
            
            # Safely parse successful response
            try:
                data = response.json() if response.content else None
            except (ValueError, TypeError):
                # If response is not JSON, return raw text
                data = response.text if response.content else None
            
            return MeliApiResponse(
                status=response.status_code,
                data=data,
                headers=dict(response.headers)
            )
            
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            # Re-raise to allow retry decorator to handle it
            raise
    
    # Public API methods
    
    async def get_category(self, category_id: str) -> Optional[MeliCategory]:
        """
        Get category information including attributes.
        
        Args:
            category_id: MELI category ID
            
        Returns:
            MeliCategory or None if not found
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"/categories/{category_id}"
        )
        
        if response.data:
            return MeliCategory(**response.data)
        
        logger.error(f"Failed to get category {category_id}: {response.error}")
        return None
    
    async def get_category_attributes(self, category_id: str) -> List[MeliRuleAttribute]:
        """
        Get all attributes for a category.
        
        Args:
            category_id: MELI category ID
            
        Returns:
            List of MeliRuleAttribute
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"/categories/{category_id}/attributes"
        )
        
        if response.data:
            return [MeliRuleAttribute(**attr) for attr in response.data]
        
        logger.error(f"Failed to get attributes for category {category_id}: {response.error}")
        return []
    
    async def get_listing_types(self) -> List[MeliListingType]:
        """
        Get available listing types for the site.
        
        Returns:
            List of MeliListingType
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"/sites/{self.site_id}/listing_types"
        )
        
        if response.data:
            return [MeliListingType(**lt) for lt in response.data]
        
        logger.error(f"Failed to get listing types: {response.error}")
        return []
    
    async def get_item_conditions(self) -> List[MeliCondition]:
        """
        Get available item conditions for the site.
        
        Returns:
            List of MeliCondition
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"/sites/{self.site_id}/item_conditions"
        )
        
        if response.data:
            return [MeliCondition(**cond) for cond in response.data]
        
        logger.error(f"Failed to get item conditions: {response.error}")
        return []
    
    async def search_categories(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for categories by name.
        
        Args:
            query: Search query
            
        Returns:
            List of category search results
            
        Raises:
            MeliApiError: If the API request fails
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"/sites/{self.site_id}/domain_discovery/search",
            params={"q": query}
        )
        
        if response.error:
            logger.error(f"Failed to search categories: {response.error.message}")
            raise MeliApiError(
                message=response.error.message,
                error=response.error.error,
                status=response.error.status,
                cause=response.error.cause
            )
        
        return response.data or []
    
    async def validate_item(self, category_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate item data against MELI rules.
        
        Args:
            category_id: Category ID
            item_data: Item data to validate
            
        Returns:
            Validation results
        """
        # Create request data with protected fields
        request_data = dict(item_data)  # Create a copy
        # Set category_id and site_id after copying to prevent override
        request_data["category_id"] = category_id
        request_data["site_id"] = self.site_id
        
        response = await self._make_request(
            method="POST",
            endpoint=f"/items/validate",
            json_data=request_data,
            authenticated=True
        )
        
        if response.data:
            return response.data
        
        if response.error:
            return {
                "valid": False,
                "errors": response.error.model_dump()
            }
        
        return {"valid": False, "errors": ["Unknown validation error"]}
    
    async def get_site_domains(self) -> List[Dict[str, Any]]:
        """
        Get all domains (top-level categories) for the site.
        
        Returns:
            List of domains
            
        Raises:
            MeliApiError: If the API request fails
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"/sites/{self.site_id}/domains"
        )
        
        # Check for errors and propagate them
        if response.error:
            logger.error(f"Failed to get site domains: {response.error.message}")
            raise MeliApiError(
                message=response.error.message,
                error=response.error.error,
                status=response.status,
                cause=response.error.cause
            )
        
        return response.data or []
