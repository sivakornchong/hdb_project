import boto3
import os
from modules.utils.logging_fn import logger

S3_client = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-east-1",
)

S3_PREFIX = "autoiteration/"
BUCKET_NAME = "hdb-predict-model"


def write_to_S3(file_path):
    try:
        filename = os.path.basename(file_path)
        s3_key = f"{S3_PREFIX}{filename}"
        S3_client.upload_file(file_path, BUCKET_NAME, s3_key)
        logger.info(f"Uploaded file from {file_path} to S3 {s3_key}")
    except Exception as e:
        logger.info(f"Error loading file to S3 {e}")


if __name__ == "__main__":
    write_to_S3("model/finalized_model2.sav")
