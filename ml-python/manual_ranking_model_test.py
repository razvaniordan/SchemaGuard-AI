import pandas as pd

from core.recommendation_ranking_model import RecommendationRankingModel


rows = []

for index in range(50):
    rows.append(
        {
            "suggestionType": "ENABLE_3DS",
            "expectedImpact": 2.0 + index * 0.1,
            "difficulty": "LOW",
            "condition": "3DS authentication",
            "amount": 100 + index,
            "category": "standard",
            "historicalSuccessRate": 0.8,
            "label_successfulRecommendation": 1,
        }
    )

for index in range(50):
    rows.append(
        {
            "suggestionType": "CHANGE_CLEARING_TIME",
            "expectedImpact": 1.0,
            "difficulty": "MEDIUM",
            "condition": "clearing time",
            "amount": 100 + index,
            "category": "standard",
            "historicalSuccessRate": 0.3,
            "label_successfulRecommendation": 0,
        }
    )

training_df = pd.DataFrame(rows)

model = RecommendationRankingModel(
    model_version="ranking-model-v1",
    min_training_records=20,
)

train_result = model.train(training_df)

print("Training result:")
print(train_result)

artifact_path = "models/artifacts/ranking-model-v1.joblib"
model.save(artifact_path)

reloaded = RecommendationRankingModel()
reloaded.load(artifact_path)

prediction = reloaded.predict_score(
    features={
        "suggestionType": "ENABLE_3DS",
        "expectedImpact": 4.0,
        "difficulty": "LOW",
        "condition": "3DS authentication",
        "amount": 1500,
        "category": "standard",
        "historicalSuccessRate": 0.8,
    },
    heuristic_score=0.5,
)

print("Prediction:")
print(prediction.model_dump())