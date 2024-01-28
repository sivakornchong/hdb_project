#!/usr/bin/bash

set -e
cd ~/hdb_project

conda env create -f environment.yaml --name HDB_pred || echo "Environment already exists"

source /home/sivakornchong/miniconda3/etc/profile.d/conda.sh
conda activate HDB_pred

echo "Start running data extraction and model optimization" >> ~/log_file.txt
rm -rf data/2024_pipe model
mkdir data/2024_pipe
mkdir model

## Run the Python script
python src/connect_api.py &&
python src/get_features.py &&
python src/regression.py

echo "Completed python scripts" >> ~/log_file.txt

echo "git add"
git add .
echo "git commit"
git commit -m "Run from GCP VM"
echo "git push"
git push

echo "Pushed to github" >> ~/log_file.txt
