"""
Telemetry emitters for different output destinations.
"""

from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import json
import asyncio
from pathlib import Path
from datetime import datetime
import aiofiles

from src.core.logging_config import get_logger
from .events import BaseEvent

logger = get_logger(__name__)


class TelemetryEmitter(ABC):
    """Abstract base class for telemetry emitters."""
    
    @abstractmethod
    async def emit(self, event: BaseEvent):
        """Emit a single event."""
        pass
    
    async def emit_batch(self, events: List[BaseEvent]):
        """
        Emit multiple events.
        Default implementation calls emit for each event.
        """
        tasks = [self.emit(event) for event in events]
        await asyncio.gather(*tasks, return_exceptions=True)


class ConsoleTelemetryEmitter(TelemetryEmitter):
    """Emitter that outputs events to console/logger."""
    
    def __init__(self, log_level: str = "INFO"):
        """
        Initialize console emitter.
        
        Args:
            log_level: Log level for telemetry events
        """
        self.log_level = log_level
    
    async def emit(self, event: BaseEvent):
        """Emit event to console."""
        event_dict = event.dict()
        log_message = f"[TELEMETRY] {event.event_type}: {json.dumps(event_dict, default=str)}"
        
        if event.severity.value == "error":
            logger.error(log_message)
        elif event.severity.value == "warning":
            logger.warning(log_message)
        elif event.severity.value == "debug":
            logger.debug(log_message)
        else:
            logger.info(log_message)


class FileTelemetryEmitter(TelemetryEmitter):
    """Emitter that outputs events to a file."""
    
    def __init__(self, file_path: str = "/tmp/validahub_telemetry.jsonl"):
        """
        Initialize file emitter.
        
        Args:
            file_path: Path to telemetry file
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def emit(self, event: BaseEvent):
        """Emit event to file."""
        try:
            async with aiofiles.open(self.file_path, mode='a') as f:
                event_json = event.json() + '\n'
                await f.write(event_json)
        except Exception as e:
            logger.error(f"Failed to write telemetry to file: {e}")
    
    async def emit_batch(self, events: List[BaseEvent]):
        """Emit multiple events to file efficiently."""
        try:
            async with aiofiles.open(self.file_path, mode='a') as f:
                lines = [event.json() + '\n' for event in events]
                await f.writelines(lines)
        except Exception as e:
            logger.error(f"Failed to write telemetry batch to file: {e}")


class KafkaTelemetryEmitter(TelemetryEmitter):
    """Emitter that sends events to Kafka."""
    
    def __init__(
        self,
        bootstrap_servers: List[str],
        topic: str = "telemetry-events",
        **kafka_config
    ):
        """
        Initialize Kafka emitter.
        
        Args:
            bootstrap_servers: List of Kafka brokers
            topic: Kafka topic for telemetry
            **kafka_config: Additional Kafka configuration
        """
        self.topic = topic
        self.producer = None
        
        try:
            from aiokafka import AIOKafkaProducer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=','.join(bootstrap_servers),
                value_serializer=lambda v: json.dumps(v, default=str).encode(),
                **kafka_config
            )
        except ImportError:
            logger.warning("aiokafka not installed, Kafka telemetry disabled")
    
    async def start(self):
        """Start Kafka producer (idempotent)."""
        if self.producer:
            try:
                await self.producer.start()
            except Exception:
                # Already started, ignore
                pass
    
    async def emit(self, event: BaseEvent):
        """Emit event to Kafka."""
        if not self.producer:
            return
        
        try:
            # Ensure producer is started (will be idempotent if already started)
            await self.start()
            
            # Send event
            await self.producer.send(
                self.topic,
                value=event.dict(),
                key=event.correlation_id.encode() if event.correlation_id else None
            )
        except Exception as e:
            logger.error(f"Failed to send telemetry to Kafka: {e}")
    
    async def emit_batch(self, events: List[BaseEvent]):
        """Emit multiple events to Kafka efficiently."""
        if not self.producer:
            return
        
        try:
            # Ensure producer is started (will be idempotent if already started)
            await self.start()
            
            # Create batch
            batch = self.producer.create_batch()
            
            for event in events:
                metadata = batch.append(
                    key=event.correlation_id.encode() if event.correlation_id else None,
                    value=json.dumps(event.dict(), default=str).encode(),
                    timestamp=None
                )
                if metadata is None:
                    # Batch is full, send it
                    await self.producer.send_batch(batch, self.topic)
                    batch = self.producer.create_batch()
                    batch.append(
                        key=event.correlation_id.encode() if event.correlation_id else None,
                        value=json.dumps(event.dict(), default=str).encode(),
                        timestamp=None
                    )
            
            # Send remaining batch
            if batch.record_count() > 0:
                await self.producer.send_batch(batch, self.topic)
                
        except Exception as e:
            logger.error(f"Failed to send telemetry batch to Kafka: {e}")
    
    async def close(self):
        """Close Kafka producer."""
        if self.producer:
            await self.producer.stop()


class HTTPTelemetryEmitter(TelemetryEmitter):
    """Emitter that sends events to an HTTP endpoint."""
    
    def __init__(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 5
    ):
        """
        Initialize HTTP emitter.
        
        Args:
            endpoint: HTTP endpoint URL
            headers: Optional headers for requests
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout
    
    async def emit(self, event: BaseEvent):
        """Emit event via HTTP."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    json=event.dict(),
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
        except ImportError:
            logger.warning("httpx not installed, HTTP telemetry disabled")
        except Exception as e:
            logger.error(f"Failed to send telemetry via HTTP: {e}")
    
    async def emit_batch(self, events: List[BaseEvent]):
        """Emit multiple events via HTTP."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                events_data = [event.dict() for event in events]
                response = await client.post(
                    self.endpoint,
                    json={"events": events_data},
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
        except ImportError:
            logger.warning("httpx not installed, HTTP telemetry disabled")
        except Exception as e:
            logger.error(f"Failed to send telemetry batch via HTTP: {e}")


class CompositeTelemetryEmitter(TelemetryEmitter):
    """Emitter that sends events to multiple destinations."""
    
    def __init__(self, emitters: List[TelemetryEmitter]):
        """
        Initialize composite emitter.
        
        Args:
            emitters: List of emitters to use
        """
        self.emitters = emitters
    
    async def emit(self, event: BaseEvent):
        """Emit event to all configured emitters."""
        tasks = [emitter.emit(event) for emitter in self.emitters]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def emit_batch(self, events: List[BaseEvent]):
        """Emit batch to all configured emitters."""
        tasks = [emitter.emit_batch(events) for emitter in self.emitters]
        await asyncio.gather(*tasks, return_exceptions=True)