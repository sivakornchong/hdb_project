from modules.connect_api import fetch_all_data
from modules.get_features import main_feature_eng

# from modules.regression import main_ml
from modules.regression_datadrift import main_ml
from modules.utils.directory_gen import get_pipeline_paths
from modules.utils.variables import resource_id, mrt_source_file, historical_data_location, experiment_name
from modules.utils.logging_fn import logger, log_file_location
from modules.utils.connection import write_log_to_s3, S3_log_PREFIX, init_mlflow
from modules.rpi_generator import main_rpi
import argparse
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run pipeline")
    parser.add_argument("--skip-extraction", action="store_true", help="Skip the extraction step if this flag is set.")
    args = parser.parse_args()

    logger.info("Running reiteration pipeline")
    paths, timestamp = get_pipeline_paths()
    logger.info("Regenerating RPI based on webscrapping data and extrapolation")
    main_rpi()
    logger.info("Connecting to MLFlow for experimental logging")
    init_mlflow(experiment_name, private_IP=False)

    if not args.skip_extraction:
        logger.info("Fetching all data from HDB in JSON format")
        fetch_all_data(resource_id, output_file=paths["json_raw"])
        logger.info("Commencing feature engineering")
        main_feature_eng(
            historical_data_location,
            json_raw=paths["json_raw"],
            mrt_source_file=mrt_source_file,
            output_file_location=paths["data_feature_file"],
        )
    else:
        logger.info("Skipping data extraction and regeneration step")

    logger.info("Running machine learning model development")
    main_ml(paths["data_feature_file"], paths["model_output"])
    logger.info("Completed training ML model")
    write_log_to_s3(S3_log_PREFIX, timestamp, log_file_location)
