## To run docker on the EC2 deployment

1. Build image based on the DockerFile
`docker build . --tag=ml_pipeline`

2. Stop existing image 
`docker stop ml_pipeline`

3. Clear the existing stopped container and image
`docker container prune`
`docker image prune`

4. Instantiate new image and run the newly created container in the background
`bash boot_prod.sh`

5. To monitor the logs of the container
`docker logs -f ml_pipeline`

## Autoiteration pipeline
1. Once the docker has completed its run, it will stop.

2. To run again, there is a cronjob that activates it the command `docker start ml_pipeline` upon startup of EC2.

3. The schedule for EC2 cstartup and shutdown is scheduled to be every 15 days by AWS CloudWatch and AWS Lambda.

## To run on development in local computer

1. Install relevant virtual environment
`pip install -r env/requirements.txt`

2. Run the bash file to inject in the environment variable
`bash boot_dev.sh`