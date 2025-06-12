docker run \
    -d \
    --name ml_pipeline \
    --restart=always \
    -e AWS_ACCESS_KEY_ID=$(awk -F "=" '/aws_access_key_id/ {print $2}' ~/.aws/credentials | tr -d ' ') \
    -e AWS_SECRET_ACCESS_KEY=$(awk -F "=" '/aws_secret_access_key/ {print $2}' ~/.aws/credentials | tr -d ' ') \
    -v ${pwd}/src:/app/src \
    -v ${pwd}/model:/app/model \
    -v ${pwd}/logs:/app/logs
    ml_pipeline