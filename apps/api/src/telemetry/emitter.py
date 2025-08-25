"""
Telemetry emitter interface and implementations.
"""

import json
import logging
from core.logging_config import get_logger
import uuid
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Protocol
from pathlib import Path

logger = get_logger(__name__)


class TelemetryEmitter(Protocol):
    """Protocol for telemetry emitters."""
    
    def emit(
        self,
        event: str,
        payload: Dict[str, Any],
        *,
        partition_key: str,
        version: str = "v1",
        correlation_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> None:
        """
        Emit a telemetry event.
        
        Args:
            event: Event name (e.g., "job.started")
            payload: Event payload data
            partition_key: Key for partitioning (e.g., "marketplace:category")
            version: Event schema version
            correlation_id: Optional correlation ID for tracing
            parent_id: Optional parent event/job ID
        """
        ...


class LoggingTelemetryEmitter:
    """Telemetry emitter that writes to structured logs."""
    
    def __init__(self, logger_name: str = "telemetry"):
        """Initialize with logger name."""
        self.logger = logging.getLogger(logger_name)
        
    def emit(
        self,
        event: str,
        payload: Dict[str, Any],
        *,
        partition_key: str,
        version: str = "v1",
        correlation_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> None:
        """Emit event to structured logs."""
        
        # Create event envelope
        envelope = {
            "event_id": str(uuid.uuid4()),  # Unique event ID for idempotency
            "event_name": event,
            "version": version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "partition_key": partition_key,
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "parent_id": parent_id,
            "payload": payload
        }
        
        # Log as structured JSON
        self.logger.info(
            f"TELEMETRY_EVENT: {event}",
            extra={
                "telemetry": envelope,
                "json": json.dumps(envelope, default=str)
            }
        )


class FileBasedTelemetryEmitter:
    """Telemetry emitter that writes to JSON files (for development/testing)."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize with output directory."""
        # Define the secure base directory
        base_dir = Path(os.path.expanduser("~/.local/share/validahub")).resolve()
        
        if output_dir is None:
            # Use default telemetry subdirectory
            output_path = (base_dir / "telemetry").resolve()
        else:
            # Validate user-provided path
            import urllib.parse
            
            # Decode any URL-encoded sequences (handles all encoding variants)
            decoded_dir = urllib.parse.unquote(output_dir, errors='strict')
            
            # Expand user home directory and resolve to absolute path
            # Path.resolve() canonicalizes the path and safely handles any '..' components
            output_path = Path(os.path.expanduser(decoded_dir)).resolve()
            
            # Ensure the resolved path is within the allowed base directory
            try:
                output_path.relative_to(base_dir)
            except ValueError:
                raise ValueError(f"Output directory must be within {base_dir}")
        
        self.output_dir = output_path
        # Create directory with restrictive permissions (0700)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.output_dir, 0o700)
        except OSError as e:
            # May fail on some systems, but directory was created
            logger.warning(
                f"Could not set permissions to 0o700 for telemetry directory {self.output_dir}: "
                f"{type(e).__name__}: {e}"
            )
        
    def emit(
        self,
        event: str,
        payload: Dict[str, Any],
        *,
        partition_key: str,
        version: str = "v1",
        correlation_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> None:
        """Write event to JSON file."""
        
        # Create event envelope
        event_id = str(uuid.uuid4())
        envelope = {
            "event_id": event_id,
            "event_name": event,
            "version": version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "partition_key": partition_key,
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "parent_id": parent_id,
            "payload": payload
        }
        
        # Write to file
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{event}_{event_id[:8]}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(envelope, f, indent=2, default=str)
            
        logger.debug(f"Wrote telemetry event to {filepath}")


class HTTPTelemetryEmitter:
    """Telemetry emitter that sends events via HTTP."""
    
    def __init__(self, endpoint: str, api_key: Optional[str] = None):
        """Initialize with HTTP endpoint."""
        import httpx
        
        self.endpoint = endpoint
        self.api_key = api_key
        # Create a reusable async client
        self.client = httpx.AsyncClient(timeout=5.0)
        
    async def emit(
        self,
        event: str,
        payload: Dict[str, Any],
        *,
        partition_key: str,
        version: str = "v1",
        correlation_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> None:
        """Send event via HTTP POST."""
        
        # Create event envelope
        envelope = {
            "event_id": str(uuid.uuid4()),
            "event_name": event,
            "version": version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "partition_key": partition_key,
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "parent_id": parent_id,
            "payload": payload
        }
        
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        try:
            response = await self.client.post(
                self.endpoint,
                json=envelope,
                headers=headers
            )
            response.raise_for_status()
            logger.debug(f"Successfully sent telemetry event {event} to {self.endpoint}")
        except Exception as e:
            logger.error(f"Failed to send telemetry event: {e}")
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Enter the async context manager."""
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        """Exit the async context manager and close the client."""
        await self.close()
    
    def __del__(self):
        """Ensure client is closed on deletion."""
        try:
            import asyncio
            if self.client and not self.client.is_closed:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self.client.aclose())
                except RuntimeError:
                    # No running loop, can't close async client
                    pass
        except Exception:
            pass


class CompositeTelemetryEmitter:
    """Emitter that sends to multiple destinations."""
    
    def __init__(self, emitters: list):
        """Initialize with list of emitters."""
        self.emitters = emitters
        
    def emit(
        self,
        event: str,
        payload: Dict[str, Any],
        *,
        partition_key: str,
        version: str = "v1",
        correlation_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> None:
        """Emit to all configured emitters."""
        
        for emitter in self.emitters:
            try:
                emitter.emit(
                    event=event,
                    payload=payload,
                    partition_key=partition_key,
                    version=version,
                    correlation_id=correlation_id,
                    parent_id=parent_id
                )
            except Exception as e:
                logger.error(f"Failed to emit to {emitter.__class__.__name__}: {e}")


class NoOpTelemetryEmitter:
    """No-operation emitter for testing or when telemetry is disabled."""
    
    def emit(
        self,
        event: str,
        payload: Dict[str, Any],
        *,
        partition_key: str,
        version: str = "v1",
        correlation_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> None:
        """Do nothing."""
        pass


# Global emitter instance
_telemetry_emitter: Optional[TelemetryEmitter] = None


def get_telemetry_emitter() -> TelemetryEmitter:
    """Get or create global telemetry emitter."""
    global _telemetry_emitter
    
    if _telemetry_emitter is None:
        # Configure based on environment
        import os
        
        if os.getenv("TELEMETRY_DISABLED", "").lower() == "true":
            _telemetry_emitter = NoOpTelemetryEmitter()
        elif os.getenv("TELEMETRY_HTTP_ENDPOINT"):
            _telemetry_emitter = HTTPTelemetryEmitter(
                endpoint=os.getenv("TELEMETRY_HTTP_ENDPOINT"),
                api_key=os.getenv("TELEMETRY_API_KEY")
            )
        elif os.getenv("TELEMETRY_FILE_DIR"):
            _telemetry_emitter = FileBasedTelemetryEmitter(
                output_dir=os.getenv("TELEMETRY_FILE_DIR")
            )
        else:
            # Default to logging
            _telemetry_emitter = LoggingTelemetryEmitter()
            
    return _telemetry_emitter


def set_telemetry_emitter(emitter: TelemetryEmitter) -> None:
    """Set global telemetry emitter (for testing)."""
    global _telemetry_emitter
    _telemetry_emitter = emitter