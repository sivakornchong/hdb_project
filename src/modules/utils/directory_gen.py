import os
from datetime import datetime
from modules.utils.logging_fn import logger


def get_pipeline_paths(base_dir="data") -> dict:
    current_year = datetime.now().year
    year_dir = f"{current_year}_pipe"
    model_timestamp = datetime.now().strftime("%y%m%d-%H")

    paths = {
        "json_raw": os.path.join(base_dir, year_dir, "data_source.json"),
        "data_feature_file": os.path.join(base_dir, year_dir, "data_features.json"),
        "year": current_year,
        "year_dir": os.path.join(base_dir, year_dir),
        "model_output": os.path.join("model", model_timestamp + ".sav"),
    }

    # Create log directory if it doesn't exist

    data_path = os.path.join(base_dir, year_dir)
    if not os.path.exists(data_path):
        os.makedirs(data_path, exist_ok=True)
        logger.info("Created data path for the file")

    logger.info(paths)
    return paths
