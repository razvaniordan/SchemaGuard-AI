import pandas as pd

from core.impact_prediction_model import ImpactPredictionModel
from core.recommendation_ranking_model import RecommendationRankingModel

df = pd.read_csv("data/training_data.csv")

impact_model = ImpactPredictionModel(
    model_version="impact-model-v1",
    min_training_records=20,
)

impact_result = impact_model.train(df)
print("Impact model:", impact_result)

if impact_result["trained"]:
    impact_model.save("models/artifacts/impact-model-v1.joblib")

ranking_model = RecommendationRankingModel(
    model_version="ranking-model-v1",
    min_training_records=20,
)

ranking_result = ranking_model.train(df)
print("Ranking model:", ranking_result)

if ranking_result["trained"]:
    ranking_model.save("models/artifacts/ranking-model-v1.joblib")