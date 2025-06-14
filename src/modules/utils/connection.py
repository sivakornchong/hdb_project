import boto3
import os
from modules.utils.logging_fn import logger
import mlflow


S3_client = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-east-1",
)

S3_model_PREFIX = "autoiteration/model/"
S3_log_PREFIX = "autoiteration/logs/"
BUCKET_NAME = "hdb-predict-model"


PRIVATE_IP_MLFLOW_SERVER = "http://172.31.62.85:5000"
PUBLIC_IP_MLFLOW_SERVER = "http://54.227.128.118:5000"


def init_mlflow(name, private_IP=True):
    if private_IP:
        mlflow.set_tracking_uri(PRIVATE_IP_MLFLOW_SERVER)
    else:
        mlflow.set_tracking_uri(PUBLIC_IP_MLFLOW_SERVER)
    mlflow.set_experiment(name)
    logger.info(f"Initialize the MLFlow run with name {name}")


def write_to_s3(PREFIX, file_path):
    try:
        filename = os.path.basename(file_path)
        s3_key = f"{PREFIX}{filename}"
        S3_client.upload_file(file_path, BUCKET_NAME, s3_key)
        logger.info(f"Uploaded file from {file_path} to S3 {s3_key}")
    except Exception as e:
        logger.info(f"Error loading file to S3 {e}")


def write_log_to_s3(PREFIX, timestamp, file_path):
    try:
        filename = os.path.basename(file_path)
        s3_key = f"{PREFIX}{timestamp}{filename}"
        S3_client.upload_file(file_path, BUCKET_NAME, s3_key)
        logger.info(f"Uploaded file from {file_path} to S3 {s3_key}")
    except Exception as e:
        logger.info(f"Error loading file to S3 {e}")
