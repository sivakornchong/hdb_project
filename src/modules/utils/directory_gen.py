import os
from datetime import datetime
from modules.utils.logging_fn import logger


def get_pipeline_paths(base_dir="data") -> dict:
    current_year = datetime.now().year
    year_dir = f"{current_year}_pipe"

    paths = {
        "json_raw": os.path.join(base_dir, year_dir, "data_source.json"),
        "data_feature_file": os.path.join(base_dir, year_dir, "data_features.json"),
        "year": current_year,
        "year_dir": os.path.join(base_dir, year_dir),
    }

    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.join(base_dir, year_dir)), exist_ok=True)

    logger.info(paths)
    return paths
