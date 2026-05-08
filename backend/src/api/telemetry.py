"""Azure Monitor OpenTelemetry setup for the audit agent API."""

import os
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

logger = logging.getLogger("audit-agent-telemetry")


def setup_telemetry():
    """Configures Azure Monitor OpenTelemetry.
    
    Auto-instruments FastAPI requests, dependency calls, and logging.
    Silently skips if connection string is not configured.
    """
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logger.warning("APPLICATIONINSIGHTS_CONNECTION_STRING not set. Telemetry disabled.")
        return

    try:
        configure_azure_monitor(
            connection_string=connection_string,
            logger_name="audit-agent-tracer"
        )
        logger.info("Azure Monitor telemetry enabled.")
    except Exception as e:
        logger.error(f"Azure Monitor initialization failed: {e}")