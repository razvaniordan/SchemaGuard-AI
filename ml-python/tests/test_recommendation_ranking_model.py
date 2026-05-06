import pandas as pd

from core.recommendation_ranking_model import RecommendationRankingModel


def test_small_dataset_falls_back_from_training():
    model = RecommendationRankingModel(min_training_records=20)

    df = pd.DataFrame(
        [
            {
                "suggestionType": "ENABLE_3DS",
                "expectedImpact": 2.0,
                "difficulty": "LOW",
                "condition": "3DS authentication",
                "amount": 100,
                "category": "standard",
                "historicalSuccessRate": 0.8,
                "label_successfulRecommendation": 1,
            }
        ]
    )

    result = model.train(df)

    assert result["trained"] is False
    assert "Small dataset" in result["warnings"][0]


def test_model_can_train_and_rank():
    rows = []

    for index in range(30):
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

    df = pd.DataFrame(rows)

    model = RecommendationRankingModel(min_training_records=20)
    train_result = model.train(df)

    assert train_result["trained"] is True

    prediction = model.predict_score(
        features={
            "suggestionType": "ENABLE_3DS",
            "expectedImpact": 3.0,
            "difficulty": "LOW",
            "condition": "3DS authentication",
            "amount": 150,
            "category": "standard",
            "historicalSuccessRate": 0.8,
        },
        heuristic_score=0.5,
    )

    assert prediction.fallbackUsed is False
    assert prediction.score >= 0
    assert prediction.modelConfidence >= 0.65
    assert prediction.modelVersion == "ranking-model-v1"


def test_missing_features_falls_back():
    model = RecommendationRankingModel(min_training_records=1)

    df = pd.DataFrame(
        [
            {
                "suggestionType": "ENABLE_3DS",
                "expectedImpact": 2.0,
                "difficulty": "LOW",
                "condition": "3DS authentication",
                "amount": 100,
                "category": "standard",
                "historicalSuccessRate": 0.8,
                "label_successfulRecommendation": 1,
            }
        ]
    )

    model.train(df)

    prediction = model.predict_score(
        features={
            "suggestionType": "ENABLE_3DS",
            "expectedImpact": 2.0,
        },
        heuristic_score=0.75,
    )

    assert prediction.fallbackUsed is True
    assert prediction.score == 0.75
    assert "Missing required features" in prediction.warnings[0]


def test_model_can_save_and_reload(tmp_path):
    rows = []

    for index in range(30):
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

    artifact_path = tmp_path / "ranking-model-v1.joblib"

    model = RecommendationRankingModel(min_training_records=20)
    model.train(pd.DataFrame(rows))
    model.save(str(artifact_path))

    reloaded = RecommendationRankingModel()
    reloaded.load(str(artifact_path))

    prediction = reloaded.predict_score(
        features={
            "suggestionType": "ENABLE_3DS",
            "expectedImpact": 3.0,
            "difficulty": "LOW",
            "condition": "3DS authentication",
            "amount": 150,
            "category": "standard",
            "historicalSuccessRate": 0.8,
        },
        heuristic_score=0.5,
    )

    assert prediction.fallbackUsed is False
    assert prediction.modelVersion == "ranking-model-v1"