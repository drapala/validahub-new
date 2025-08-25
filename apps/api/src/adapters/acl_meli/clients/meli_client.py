"""
HTTP client for Mercado Livre API.
Handles authentication, rate limiting, and API communication.
"""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import time

from core.logging_config import get_logger
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
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_second: float = 10):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
    
    async def wait(self):
        """Wait if necessary to respect rate limit."""
        current = time.time()
        elapsed = current - self.last_call
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_call = time.time()


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
                        wait_time = backoff_factor ** attempt
                        logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
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
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=httpx.Timeout(30.0),
            headers={
                "User-Agent": "ValidaHub/1.0",
                "Accept": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token."""
        if self.access_token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at:
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
            data = response.json()
            
            self.access_token = data["access_token"]
            expires_in = data.get("expires_in", 21600)  # Default 6 hours
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
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
                error_data = response.json() if response.content else {}
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
            
            return MeliApiResponse(
                status=response.status_code,
                data=response.json() if response.content else None,
                headers=dict(response.headers)
            )
            
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            return MeliApiResponse(
                status=0,
                error=MeliApiError(
                    message=str(e),
                    error="REQUEST_ERROR",
                    status=0
                )
            )
    
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
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"/sites/{self.site_id}/domain_discovery/search",
            params={"q": query}
        )
        
        if response.data:
            return response.data
        
        logger.error(f"Failed to search categories: {response.error}")
        return []
    
    async def validate_item(self, category_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate item data against MELI rules.
        
        Args:
            category_id: Category ID
            item_data: Item data to validate
            
        Returns:
            Validation results
        """
        response = await self._make_request(
            method="POST",
            endpoint=f"/items/validate",
            json_data={
                "category_id": category_id,
                "site_id": self.site_id,
                **item_data
            },
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
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"/sites/{self.site_id}/domains"
        )
        
        return response.data or []