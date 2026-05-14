#!/bin/sh

set -e

mkdir -p /app/data
mkdir -p /app/models/artifacts

echo "Checking ML artifacts..."

if [ ! -f "/app/models/artifacts/fraud_model.joblib" ] || \
   [ ! -f "/app/models/artifacts/anomaly_model.joblib" ] || \
   [ ! -f "/app/models/artifacts/root_cause_model.joblib" ]; then

  echo "No trained models found. Training models..."

  python generate_training_data.py
  python train_models.py
  python train_anomaly_model.py
  python train_root_cause_model.py

  echo "Training completed."
else
  echo "Models already exist. Skipping training."
fi

echo "Starting ML API..."

exec uvicorn main:app --host 0.0.0.0 --port 8001