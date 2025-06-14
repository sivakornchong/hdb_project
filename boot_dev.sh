# This script is meant to run for local development in a non-containerized environment
# Assume that there is credientials at ~/.aws/credentials

export AWS_ACCESS_KEY_ID=$(awk -F "=" '/aws_access_key_id/ {print $2}' ~/.aws/credentials | tr -d ' ')
export AWS_SECRET_ACCESS_KEY=$(awk -F "=" '/aws_secret_access_key/ {print $2}' ~/.aws/credentials | tr -d ' ')


if [ "$1" = "--skip-extraction" ]; then
    python src/main.py --skip-extraction
else
    python src/main.py
fi

# To run skipping extraction: ./boot_dev --skip-extraction