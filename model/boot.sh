
rm -r data/2024_pipe model
mkdir data/2024_pipe
mkdir model

# Run the Python script
python src/connect_api.py &&
python src/get_features.py &&
python src/regression.py