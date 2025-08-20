"""
Shared constants used across the application.
"""

# Job parameter keys
PARAM_MARKETPLACE = "marketplace"
PARAM_CATEGORY = "category"
PARAM_REGION = "region"
PARAM_INPUT_URI = "input_uri"
PARAM_RULESET = "ruleset"
PARAM_ANALYSIS_TYPE = "analysis_type"
PARAM_JOB_ID = "job_id"
PARAM_FORMAT = "format"

# Default values
DEFAULT_MARKETPLACE = "unknown"
DEFAULT_CATEGORY = "unknown"
DEFAULT_REGION = "default"
DEFAULT_RULESET = "default"

# Limits
MAX_RETRY_COUNT = 3
MAX_PRIORITY = 10
MIN_PRIORITY = 1

# Queue names (base names, actual format determined by QueueConfig)
QUEUE_FREE = "queue:free"
QUEUE_PRO = "queue:pro"
QUEUE_BUSINESS = "queue:business"
QUEUE_ENTERPRISE = "queue:enterprise"