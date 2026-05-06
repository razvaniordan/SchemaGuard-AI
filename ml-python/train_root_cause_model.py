import pandas as pd

from core.root_cause_driver_model import RootCauseDriverModel


df = pd.read_csv("data/training_data.csv")

model = RootCauseDriverModel(
    model_version="root-cause-model-v1",
    min_training_records=100,
    high_loss_threshold=5.0,
    random_state=42,
)

result = model.train(df)

print("Root cause model:", result)

if result["trained"]:
    model.save("models/artifacts/root-cause-model-v1.joblib")