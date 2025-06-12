import logging
import os

log_file_location = "logs/pipeline.log"


def setup_logger(log_file=log_file_location, level=logging.INFO):
    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],  # Also logs to stdout
    )

    logger = logging.getLogger("pipeline")

    return logger


logger = setup_logger()
