import os
from datetime import datetime


def get_pipeline_paths(base_dir="data") -> dict:
    current_year = datetime.now().year
    year_dir = f"{current_year}_pipe"

    paths = {
        "json_raw": os.path.join(base_dir, year_dir, "data_source.json"),
        "data_feature_file": os.path.join(base_dir, year_dir, "data_features.json"),
        "year": current_year,
        "year_dir": os.path.join(base_dir, year_dir),
    }

    print(paths)
    return paths
