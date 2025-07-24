import structlog, logging
from structlog.stdlib import LoggerFactory

def configure_logging():
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    structlog.configure(
        logger_factory=LoggerFactory(),
        processors=[
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ]
    )

logger = structlog.get_logger()

configure_logging()

