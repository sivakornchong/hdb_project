from modules.utils.variables import (
    numeric_features,
    categorical_features,
    test_months,
)
from modules.utils.logging_fn import logger
import mlflow
import warnings
from math import sqrt
from modules.ml.data_setup import df_loading_dd, df_timecut_dd
from modules.ml.model_pipeline import build_preprocessor, hyperparam_opt, final_fit
import pandas as pd
from dateutil.relativedelta import relativedelta

warnings.filterwarnings("ignore", category=UserWarning)


def generate_timelist(model_data):
    transaction_dates = pd.to_datetime(model_data["transaction"].unique())
    transaction_dates = sorted(transaction_dates)

    max_time = max(transaction_dates)
    cutoff_time = max_time - relativedelta(months=test_months)

    start_times = []
    end_times = []
    last_added = None
    for date in transaction_dates:
        if date.year < 2023:
            if last_added is not None and (date - last_added).days < 115:
                continue
        end_time = date + relativedelta(months=12)
        if end_time <= cutoff_time:
            start_times.append(date)
            end_times.append(end_time)
            last_added = date

    return start_times, end_times


def main_ml(data_feature_file, model_filename):
    model_data = df_loading_dd(data_feature_file)
    start_times, end_times = generate_timelist(model_data)
    logger.info("Running data drift experiment")

    for i in range(len(start_times)):
        with mlflow.start_run(run_name=f"Train {start_times[i].date()} to {end_times[i].date()}"):
            logger.info(f"Training for trainset {start_times[i].date()} to {end_times[i].date()}")
            mlflow.log_param("train_start_date", start_times[i].date())
            mlflow.log_param("experiment_index", i)
            X_train, X_test, y_train, y_test = df_timecut_dd(model_data, start_times[i], end_times[i])
            preprocess = build_preprocessor(numeric_features, categorical_features)
            xgb_random_search = hyperparam_opt(preprocess, X_train, y_train)
            mlflow.set_tag("Optimized parameter", xgb_random_search)
            pipe_xgb_opt = final_fit(
                xgb_random_search, preprocess, X_train, y_train, X_test, y_test, model_filename=model_filename
            )
