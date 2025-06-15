import pandas as pd
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_squared_error
import xgboost as xgb
from modules.utils.variables import (
    relevant_columns_ml,
    numeric_features,
    categorical_features,
    model_filename,
    data_feature_file,
    test_size,
    target_col,
    split_rand,
    test_months,
)
import pickle
from modules.utils.logging_fn import setup_logger, logger
from modules.utils.connection import write_to_s3, S3_model_PREFIX
import mlflow
import mlflow.data
from mlflow.data.pandas_dataset import PandasDataset
from mlflow.models.signature import infer_signature
from dateutil.relativedelta import relativedelta
import warnings
from math import sqrt

warnings.filterwarnings("ignore", category=UserWarning)


def split_random(model_data, test_size):

    X = model_data.drop(target_col, axis=1)
    y = model_data[target_col]

    mlflow.set_tag("Test set start", X["transaction"].min())
    mlflow.set_tag("Test set end", X["transaction"].max())
    mlflow.set_tag("Train set start", X["transaction"].min())
    mlflow.set_tag("Train set end", X["transaction"].max())
    mlflow.set_tag("Test ratio", test_size)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=573)
    return X_train, X_test, y_train, y_test


def split_date(dataset, test_months):
    dataset2 = dataset.copy()

    dataset2 = dataset2.sort_values(by="transaction")  # ensure sorted by date
    cutoff_date = dataset2["transaction"].max() - relativedelta(months=test_months)

    test_df = dataset2[dataset2["transaction"] > cutoff_date].sample(frac=1)
    train_df = dataset2[dataset2["transaction"] <= cutoff_date].sample(frac=1)

    mlflow.set_tag("Test set start", cutoff_date)
    mlflow.set_tag("Test set end", dataset2["transaction"].max())
    mlflow.set_tag("Train set start", dataset2["transaction"].min())
    mlflow.set_tag("Train set end", dataset2["transaction"].min())
    mlflow.set_tag("Test ratio", test_df.shape[0] / dataset2.shape[0])

    X_train = train_df.drop(columns=target_col)
    y_train = train_df[target_col]

    X_test = test_df.drop(columns=target_col)
    y_test = test_df[target_col]

    return X_train, X_test, y_train, y_test


def mlflow_logdataset(name: str, model_data: pd.DataFrame, target_col=None, artefact=False):
    model_dataset: PandasDataset = mlflow.data.from_pandas(model_data, targets=target_col)
    mlflow.log_input(model_dataset, context=name)

    if artefact:
        pass  # TODO: send artefact to S3


def df_prepraration(data_feature_file, split_rand=split_rand):
    df = pd.read_json(data_feature_file, lines=True)
    df = df.sample(frac=1, random_state=42)

    df_chosen = df[relevant_columns_ml].copy()
    df_chosen = df_chosen[df_chosen["Postal"] != "NIL"]  # remove the items with no postal code#
    df_chosen["Postal"] = df_chosen["Postal"].astype(int)  # convert to int

    df_chosen["transaction"] = pd.to_datetime(df_chosen["transaction"], format="%Y-%m")

    logger.info(f"{df_chosen.shape[0]} filtered out of: {df.shape[0]}")

    # Create train and test sets
    model_data = df_chosen.copy()

    mlflow_logdataset("All data", model_data, target_col=target_col)

    # Add tag whether the split is random or by month
    if split_rand:
        mlflow.set_tag("Split Method", "Random")
        X_train, X_test, y_train, y_test = split_random(model_data, test_size=test_size)
    else:
        mlflow.set_tag("Split Method", "By date")
        X_train, X_test, y_train, y_test = split_date(model_data, test_months=test_months)

    mlflow_logdataset("Train data", X_train)
    mlflow_logdataset("Test data", X_test)

    return X_train, X_test, y_train, y_test


def build_preprocessor(numeric_features, categorical_features):
    numeric_transformer = StandardScaler()
    categorical_transformer = make_pipeline(OneHotEncoder(handle_unknown="ignore", sparse_output=False))

    preprocess = make_column_transformer(
        (numeric_transformer, numeric_features),
        (categorical_transformer, categorical_features),
    )
    return preprocess

    # From the evaluation in the notebook (regression_nb.ipynb), we will use XGBoost since it has the second highest test_r2 after randomforest.
    # However, the much smaller gap between test R2 and train R2 when compared to randomforest suggests that this model is less prone to overfitting.


def hyperparam_opt(preprocess, X_train, y_train):
    # Optimize the hyperparameters
    pipe_xgb = make_pipeline(preprocess, xgb.XGBRegressor())

    param_grid = {
        "xgbregressor__gamma": [0, 1, 10, 20, 100],
        "xgbregressor__max_depth": [3, 4, 5, 6, 7],
    }
    xgb_random_search = RandomizedSearchCV(
        pipe_xgb,
        param_distributions=param_grid,
        n_iter=10,
        n_jobs=-1,
        return_train_score=True,
    )
    xgb_random_search.fit(X_train, y_train)

    return xgb_random_search


def final_fit(xgb_random_search, preprocess, X_train, y_train, X_test, y_test, model_filename, save=True):
    # Choose the best hyperparameter for the XGBoost model
    opt_params = xgb_random_search.best_params_
    pipe_xgb_opt = make_pipeline(
        preprocess,
        xgb.XGBRegressor(
            max_depth=opt_params["xgbregressor__max_depth"],
            gamma=opt_params["xgbregressor__gamma"],
        ),
    )
    pipe_xgb_opt.fit(X_train, y_train)

    r2_score = pipe_xgb_opt.score(X_test, y_test)

    # Test of the test datasets
    logger.info(
        f"Utilizing the xgbregressor model with max_depth at {opt_params['xgbregressor__max_depth']} and gamama at {opt_params['xgbregressor__gamma']}"
    )
    logger.info(f"Final model score on test dataset is: {r2_score}")

    # Log metric (not just score)

    y_pred = pipe_xgb_opt.predict(X_test)
    test_mse = sqrt(mean_squared_error(y_test, y_pred))
    y_pred = pipe_xgb_opt.predict(X_train)
    train_mse = sqrt(mean_squared_error(y_train, y_pred))

    mlflow.log_metric("Test MSE", test_mse)
    mlflow.log_metric("Train MSE", train_mse)
    mlflow.log_metric("Test R2", r2_score)

    if save:
        pickle.dump(pipe_xgb_opt, open(model_filename, "wb"))
        logger.info("Model file saved")

        # Log final location of model via MLFlow, sending to S3
        signature = infer_signature(X_train, pipe_xgb_opt.predict(X_train))
        mlflow.sklearn.log_model(pipe_xgb_opt, name="xgb_model", signature=signature, input_example=X_train.iloc[:5])
        artifact_uri = mlflow.get_artifact_uri("xgb_model")
        logger.info("Frinal model is saved to {artifact_uri}")

    # Get run info
    run = mlflow.active_run()
    run_id = run.info.run_id
    experiment_id = run.info.experiment_id
    tracking_url = mlflow.get_tracking_uri()

    ui_url = f"{tracking_url}/#/experiments/{experiment_id}/runs/{run_id}"

    logger.info(f"Experiment results are tracked in {ui_url}")

    return pipe_xgb_opt


def main_ml(data_feature_file, model_filename):
    X_train, X_test, y_train, y_test = df_prepraration(data_feature_file)
    preprocess = build_preprocessor(numeric_features, categorical_features)
    xgb_random_search = hyperparam_opt(preprocess, X_train, y_train)
    mlflow.set_tag("Optimized parameter", xgb_random_search)
    pipe_xgb_opt = final_fit(
        xgb_random_search, preprocess, X_train, y_train, X_test, y_test, model_filename=model_filename
    )

    # write_to_s3(S3_model_PREFIX, model_filename)  ## Replaced by MLFlow
    return pipe_xgb_opt


if __name__ == "__main__":
    setup_logger("logs/ml_only.log")
    main_ml(data_feature_file, model_filename)
