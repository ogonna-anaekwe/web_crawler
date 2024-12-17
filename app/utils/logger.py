import logging


def logger() -> logging.Logger:
    """Configures (the level for) logs."""
    fmt = "%(levelname)s %(asctime)s %(pathname)s:%(lineno)d %(message)s"
    datefmt = "%m/%d/%Y %I:%M:%S %p"
    logging.basicConfig(format=fmt, datefmt=datefmt)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger


LOG = logger()
