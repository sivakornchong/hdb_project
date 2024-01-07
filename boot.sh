cd ~/hdb_project

source /home/sivakornchong/miniconda3/etc/profile.d/conda.sh
conda activate HDB_project

rm -r data/2024_pipe model
mkdir data/2024_pipe
mkdir model

## Run the Python script
python src/connect_api.py &&
python src/get_features.py &&
python src/regression.py

echo "git add"
git add .
echo "git commit"
git commit -m "Run from GCP VM"
echo "git push"
git push
