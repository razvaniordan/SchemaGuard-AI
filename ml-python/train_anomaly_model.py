import pandas as pd

from core.ml_anomaly_detection_model import MLAnomalyDetectionModel


df = pd.read_csv("data/training_data.csv")

model = MLAnomalyDetectionModel(
    model_version="anomaly-model-v1",
    contamination=0.15,
    min_training_records=100,
    random_state=42,
)

result = model.train(df)

print("Anomaly model:", result)

if result["trained"]:
    model.save("models/artifacts/anomaly-model-v1.joblib")