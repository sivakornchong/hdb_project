import pandas as pd
from sklearn.model_selection import train_test_split
from modules.utils.variables import relevant_columns_ml, test_size, target_col, split_rand, test_months
from modules.utils.logging_fn import logger
import mlflow
from mlflow.data.pandas_dataset import PandasDataset
from dateutil.relativedelta import relativedelta


## For base regular iteration
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

    mlflow.set_tag("Test set start", test_df["transaction"].min())
    mlflow.set_tag("Test set end", test_df["transaction"].max())
    mlflow.set_tag("Train set start", train_df["transaction"].min())
    mlflow.set_tag("Train set end", train_df["transaction"].max())
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


def df_preparation(data_feature_file, split_rand=split_rand):
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


## For Data drift study


def split_date_dd(dataset, start_date, end_date, test_months):
    dataset2 = dataset.copy()

    dataset2 = dataset2.sort_values(by="transaction")  # ensure sorted by date
    cutoff_date = dataset2["transaction"].max() - relativedelta(months=test_months)

    test_df = dataset2[dataset2["transaction"] > cutoff_date].sample(frac=1)
    train_df = dataset2[dataset2["transaction"] <= cutoff_date]

    train_df = train_df[(train_df["transaction"] > start_date) & (train_df["transaction"] <= end_date)].sample(frac=1)

    assert end_date < cutoff_date, "End date must be earlier than cutoff date"

    mlflow.set_tag("Test set start", test_df["transaction"].min())
    mlflow.set_tag("Test set end", test_df["transaction"].max())
    mlflow.set_tag("Train set start", train_df["transaction"].min())
    mlflow.set_tag("Train set end", train_df["transaction"].max())
    mlflow.set_tag("Test ratio", test_df.shape[0] / dataset2.shape[0])

    X_train = train_df.drop(columns=target_col)
    y_train = train_df[target_col]

    X_test = test_df.drop(columns=target_col)
    y_test = test_df[target_col]

    return X_train, X_test, y_train, y_test


def df_loading_dd(data_feature_file):
    df = pd.read_json(data_feature_file, lines=True)
    df = df.sample(frac=1, random_state=42)

    df_chosen = df[relevant_columns_ml].copy()
    df_chosen = df_chosen[df_chosen["Postal"] != "NIL"]  # remove the items with no postal code#
    df_chosen["Postal"] = df_chosen["Postal"].astype(int)  # convert to int

    df_chosen["transaction"] = pd.to_datetime(df_chosen["transaction"], format="%Y-%m")

    logger.info(f"{df_chosen.shape[0]} filtered out of: {df.shape[0]}")

    # Create train and test sets
    model_data = df_chosen.copy()

    return model_data


def df_timecut_dd(model_data, start_date, end_date):

    mlflow_logdataset("All data", model_data, target_col=target_col)

    # Add tag whether the split is random or by month
    mlflow.set_tag("Split Method", "By date")
    X_train, X_test, y_train, y_test = split_date_dd(model_data, start_date, end_date, test_months)

    mlflow_logdataset("Train data", X_train)
    mlflow_logdataset("Test data", X_test)

    return X_train, X_test, y_train, y_test
