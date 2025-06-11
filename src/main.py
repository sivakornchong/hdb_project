from modules.connect_api import fetch_all_data
from modules.get_features import main_feature_eng
from modules.regression import main_ml
from modules.utils.directory_gen import get_pipeline_paths
from modules.utils.variables import model_filename, resource_id, mrt_source_file, historical_data_location

if __name__ == "__main__":
    paths = get_pipeline_paths()
    fetch_all_data(resource_id, output_file=paths["json_raw"])
    main_feature_eng(
        historical_data_location,
        json_raw=paths["json_raw"],
        mrt_source_file=mrt_source_file,
        output_file_location=paths["data_feature_file"],
    )
    main_ml(paths["data_feature_file"], model_filename)
