import logging

from app.core.constants import constants

logging.basicConfig(
    level=getattr(logging, constants.logger.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

def get_logger(name: str) -> logging.Logger:
    """Return a consistently configured logger for a module.

    Args:
        name: The logger name, normally the importing module's dotted path.

    Returns:
        A standard-library logger using the application-wide configuration.
    """
    return logging.getLogger(name)


logger = get_logger(__name__)
