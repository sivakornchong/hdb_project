import pandas as pd
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import pickle
from modules.utils.logging_fn import logger
import mlflow
from mlflow.models.signature import infer_signature
from math import sqrt


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
        logger.info(f"Final model is saved to {artifact_uri}")

    # Get run info
    run = mlflow.active_run()
    run_id = run.info.run_id
    experiment_id = run.info.experiment_id
    tracking_url = mlflow.get_tracking_uri()

    ui_url = f"{tracking_url}/#/experiments/{experiment_id}/runs/{run_id}"

    logger.info(f"Experiment results are tracked in {ui_url}")

    return pipe_xgb_opt
