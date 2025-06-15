from modules.utils.variables import (
    numeric_features,
    categorical_features,
    model_filename,
    data_feature_file,
)
from modules.utils.logging_fn import setup_logger, logger
import mlflow
import warnings
from math import sqrt
from modules.ml.data_setup import df_preparation
from modules.ml.model_pipeline import build_preprocessor, hyperparam_opt, final_fit

warnings.filterwarnings("ignore", category=UserWarning)


def main_ml(data_feature_file, model_filename):
    X_train, X_test, y_train, y_test = df_preparation(data_feature_file)
    preprocess = build_preprocessor(numeric_features, categorical_features)
    xgb_random_search = hyperparam_opt(preprocess, X_train, y_train)
    mlflow.set_tag("Optimized parameter", xgb_random_search)
    pipe_xgb_opt = final_fit(
        xgb_random_search, preprocess, X_train, y_train, X_test, y_test, model_filename=model_filename
    )

    # write_to_s3(S3_model_PREFIX, model_filename)  ## Replaced by MLFlow


if __name__ == "__main__":
    setup_logger("logs/ml_only.log")
    main_ml(data_feature_file, model_filename)
