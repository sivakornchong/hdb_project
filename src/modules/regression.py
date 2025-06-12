import pandas as pd
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import RandomizedSearchCV
import xgboost as xgb
from modules.utils.variables import (
    relevant_columns_ml,
    numeric_features,
    categorical_features,
    model_filename,
    data_feature_file,
)
import pickle
from modules.utils.logging_fn import setup_logger, logger
from modules.utils.connection import write_to_S3


def df_prepraration(data_feature_file):
    df = pd.read_json(data_feature_file, lines=True)
    df = df.sample(frac=1, random_state=42)

    df_chosen = df[relevant_columns_ml].copy()
    df_chosen = df_chosen[df_chosen["Postal"] != "NIL"]  # remove the items with no postal code#
    df_chosen["Postal"] = df_chosen["Postal"].astype(int)  # convert to int

    logger.info(f"{df_chosen.shape[0]} filtered out of: {df.shape[0]}")

    # Create train and test sets
    model_data = df_chosen.copy()

    X = model_data.drop("resale_price_adj", axis=1)
    y = model_data["resale_price_adj"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=573)

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

    # Test of the test datasets
    logger.info(
        f"Utilizing the xgbregressor model with max_depth at {opt_params['xgbregressor__max_depth']} and gamama at {opt_params['xgbregressor__gamma']}"
    )
    logger.info(f"Final model score on test dataset is: {pipe_xgb_opt.score(X_test, y_test)}")

    if save:

        pickle.dump(pipe_xgb_opt, open(model_filename, "wb"))
        logger.info("Model file saved")

    return pipe_xgb_opt


def main_ml(data_feature_file, model_filename):
    X_train, X_test, y_train, y_test = df_prepraration(data_feature_file)
    preprocess = build_preprocessor(numeric_features, categorical_features)
    xgb_random_search = hyperparam_opt(preprocess, X_train, y_train)
    pipe_xgb_opt = final_fit(
        xgb_random_search, preprocess, X_train, y_train, X_test, y_test, model_filename=model_filename
    )
    write_to_S3(model_filename)
    return pipe_xgb_opt


if __name__ == "__main__":
    setup_logger("logs/ml_only.log")
    main_ml(data_feature_file, model_filename)
