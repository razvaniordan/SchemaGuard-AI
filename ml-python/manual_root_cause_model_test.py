from core.root_cause_driver_model import RootCauseDriverModel


model = RootCauseDriverModel()
model.load("models/artifacts/root-cause-model-v1.joblib")

for condition in [
    "3DS authentication",
    "clearing time",
    "MCC classification",
]:
    evidence = model.explain_condition(condition)
    print(evidence.model_dump())