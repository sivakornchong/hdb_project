## To run docker on the EC2 deployment

1. Build image based on the DockerFile
`docker build . --tag=ml_pipeline`

2. Stop existing image 
`docker stop ml_pipeline`

3. Instantiate new image and run the newly created container in the background
```shell
docker run \
-d \
--name ml_pipeline \
--rm\
-e AWS_ACCESS_KEY_ID=$(awk -F "=" '/aws_access_key_id/ {print $2}' ~/.aws/credentials | tr -d ' ') \
-e AWS_SECRET_ACCESS_KEY=$(awk -F "=" '/aws_secret_access_key/ {print $2}' ~/.aws/credentials | tr -d ' ') \
-v ${pwd}/src:/app/src \
-v ${pwd}/model:/app/model \
-v ${pwd}/logs:/app/logs \
ml_pipeline
```

4. To monitor the logs of the container
`docker logs -f ml_pipeline`