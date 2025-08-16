"""
Dependency injection configuration for validation pipeline.
Sets up validators, adapters, and pipeline based on configuration.
"""

import os
import logging
from typing import Optional

from ..core.interfaces.validation import (
    IValidator,
    IDataAdapter,
    IValidationPipeline
)
from ..core.pipeline.validation_pipeline_v2 import (
    ValidationPipelineV2,
    PandasDataAdapter
)
from .validators.rule_engine_validator import (
    RuleEngineValidator,
    MultiStrategyValidator
)
from .dependencies import get_rule_engine_service_singleton
from ..services.rule_engine_service import RuleEngineService

logger = logging.getLogger(__name__)


def get_validator() -> IValidator:
    """
    Factory function to get the configured validator.
    Based on environment configuration.
    """
    validator_type = os.environ.get("VALIDATOR_TYPE", "rule_engine").lower()
    
    if validator_type == "rule_engine":
        # Use the refactored rule engine service if available
        use_v2 = os.environ.get("USE_RULE_ENGINE_V2", "false").lower() == "true"
        
        if use_v2:
            # Use dependency-injected version
            rule_engine = get_rule_engine_service_singleton()
            validator = RuleEngineValidator(rule_engine)
            logger.info("Using RuleEngineValidator with V2 service")
        else:
            # Use legacy version for backward compatibility
            rule_engine = RuleEngineService()
            validator = RuleEngineValidator(rule_engine)
            logger.info("Using RuleEngineValidator with legacy service")
        
        return validator
    
    elif validator_type == "multi":
        # Multi-strategy validator (example)
        validators = []
        
        # Add rule engine validator
        rule_engine = RuleEngineService()
        validators.append(RuleEngineValidator(rule_engine))
        
        # Could add other validators here
        # validators.append(MLValidator())
        # validators.append(SchemaValidator())
        
        validator = MultiStrategyValidator(validators)
        logger.info(f"Using MultiStrategyValidator with {len(validators)} validators")
        
        return validator
    
    else:
        raise ValueError(f"Unknown validator type: {validator_type}")


def get_data_adapter() -> IDataAdapter:
    """
    Get the data adapter for data transformations.
    """
    adapter_type = os.environ.get("DATA_ADAPTER", "pandas").lower()
    
    if adapter_type == "pandas":
        return PandasDataAdapter()
    else:
        # Default to pandas
        logger.warning(f"Unknown adapter type {adapter_type}, using pandas")
        return PandasDataAdapter()


def get_validation_pipeline() -> IValidationPipeline:
    """
    Get the configured validation pipeline.
    Uses dependency injection to provide all components.
    """
    validator = get_validator()
    data_adapter = get_data_adapter()
    
    # Configuration from environment
    parallel_processing = os.environ.get("PIPELINE_PARALLEL", "false").lower() == "true"
    batch_size = int(os.environ.get("PIPELINE_BATCH_SIZE", "100"))
    
    pipeline = ValidationPipelineV2(
        validator=validator,
        data_adapter=data_adapter,
        parallel_processing=parallel_processing,
        batch_size=batch_size
    )
    
    logger.info(
        f"Created ValidationPipelineV2 with parallel={parallel_processing}, "
        f"batch_size={batch_size}"
    )
    
    return pipeline


# Singleton instances (optional, for performance)
_validation_pipeline: Optional[IValidationPipeline] = None


def get_validation_pipeline_singleton() -> IValidationPipeline:
    """
    Get singleton instance of validation pipeline.
    Useful for avoiding recreation on every request.
    """
    global _validation_pipeline
    
    if _validation_pipeline is None:
        _validation_pipeline = get_validation_pipeline()
    
    return _validation_pipeline


def reset_pipeline_singleton():
    """
    Reset the pipeline singleton.
    Useful for testing or configuration changes.
    """
    global _validation_pipeline
    _validation_pipeline = None
    logger.info("Pipeline singleton reset")