#!/bin/bash

LOG_FILE="/home/ec2-user/mlflow/mlflow.log"
LOCK_FILE="/tmp/mlflow-server.lock"
MLFLOW_BIN="/home/ec2-user/.local/bin/mlflow"
DB_URI="sqlite:////home/ec2-user/mlflow.db"
ARTIFACT_ROOT="s3://hdb-predict-model/mlflow/"
HOST="0.0.0.0"
PORT="5000"

# Acquire a lock to prevent multiple instances
if ( set -o noclobber; echo "$$" > "$LOCK_FILE") 2> /dev/null; then
    trap 'rm -f "$LOCK_FILE"; exit $?' INT TERM EXIT
    echo "$(date): Starting MLflow server..." >> "$LOG_FILE"
    exec "$MLFLOW_BIN" server \
        --backend-store-uri "$DB_URI" \
        --default-artifact-root "$ARTIFACT_ROOT" \
        --host "$HOST" \
        --port "$PORT" \
        >> "$LOG_FILE" 2>&1
else
    echo "$(date): MLflow server already running (lock file exists)." >> "$LOG_FILE"
fi
