from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import yaml
from sklearn.tree import DecisionTreeClassifier
from core.anomaly_detector import AnomalyDetector
from core.missed_condition_detector import MissedConditionDetector
from core.change_suggestion_engine import ChangeSuggestionEngine
from core.transaction_simulator import TransactionSimulator
from core.root_cause_analyzer import RootCauseAnalyzer
from core.historical_data_store import HistoricalDataStore
from core.training_data_builder import TrainingDataBuilder
from core.model_registry import ModelRegistry, ModelMetadata
from core.impact_prediction_model import ImpactPredictionModel
from models.analysis_models import (
    MLCoreResponse,
    RankedSuggestion,
    RuleEngineResult,
    PortfolioPatternResponse,
    AnomalyDetectionResponse,
    BulkSimulationRequest,
    BulkSimulationResponse,
    BulkSimulationSkippedTransaction,
    RootCauseAnalysisResponse,
)


class MLCore:
    def __init__(self) -> None:
        # Load configurable ML parameters from YAML
        self.config = self._load_config()

        # Component from Story 3.1
        self.detector = MissedConditionDetector()

        # Component from Story 3.2
        self.suggestion_engine = ChangeSuggestionEngine()

        # Component from Story 3.3
        self.simulator = TransactionSimulator()

        # Basic decision tree model for condition analysis
        self.decision_tree = self._train_decision_tree()

        # Registry for future algorithm plugins
        self.plugins = {}

    def analyze_transaction(
            self,
            current_result: RuleEngineResult,
            optimal_result: RuleEngineResult,
            persist_history: bool = False,
            actual_outcome: Dict[str, Any] | None = None,
            model_version: str | None = None,
    ) -> MLCoreResponse:
        # Select algorithm using A/B testing framework
        algorithm = self._select_algorithm(current_result)

        # Step 1: detect missed conditions
        analysis = self.detector.analyze(current_result, optimal_result)

        # Step 2: generate actionable suggestions
        suggestions = self.suggestion_engine.generate_suggestions(
            analysis.missedConditions
        )

        # Step 3: rank suggestions using NumPy weighted scoring
        ranked_suggestions = self._rank_suggestions(suggestions)

        # Step 4: simulate transaction using ranked suggestions
        simulation = self.simulator.simulate(
            current_result.transaction,
            ranked_suggestions,
        )

        # Step 5: detect common patterns using pandas
        detected_patterns = self._detect_patterns(analysis.missedConditions)

        # Step 6: return full ML pipeline result
        response = MLCoreResponse(
            analysis=analysis,
            rankedSuggestions=ranked_suggestions,
            simulation=simulation,
            detectedPatterns=detected_patterns,
            algorithmUsed=algorithm,
        )

        # Lazy initialization (NO __init__ changes)
        if persist_history:
            if not hasattr(self, "_historical_store"):
                self._historical_store = HistoricalDataStore()

            if not hasattr(self, "_training_builder"):
                self._training_builder = TrainingDataBuilder()

            record = self._training_builder.build_record(
                current_result=current_result,
                optimal_result=optimal_result,
                ml_response=response,
                actual_outcome=actual_outcome,
                model_version=model_version,
            )

            self._historical_store.store(record)

        return response

    def _load_config(self) -> Dict[str, Any]:
        # Find config file path
        config_path = Path(__file__).resolve().parent.parent / "config" / "ml_config.yml"

        # Load YAML configuration
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def _train_decision_tree(self) -> DecisionTreeClassifier:
        # Mock training data for Phase 1
        # Columns:
        # [threeDS_missing, clearing_late, mcc_issue, channel_issue]
        training_data = np.array(
            [
                [1, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [1, 1, 1, 0],
            ]
        )

        # Labels:
        # 0 = low priority
        # 1 = medium priority
        # 2 = high priority
        labels = np.array([2, 2, 1, 1, 1, 2])

        # Create decision tree model
        model = DecisionTreeClassifier(max_depth=3, random_state=42)

        # Train model on mock data
        model.fit(training_data, labels)

        return model

    def _rank_suggestions(
        self,
        suggestions: List[Any],
    ) -> List[RankedSuggestion]:
        # Read scoring weights from config
        weights = self.config["scoring"]["weights"]

        # Read difficulty score mapping from config
        difficulty_scores = self.config["difficulty_scores"]

        ranked = []

        for suggestion in suggestions:
            # Convert difficulty text to numeric value
            difficulty_score = difficulty_scores.get(suggestion.difficulty, 0.3)

            # NumPy weighted sum:
            # score = impact_weight * impact
            #       + confidence_weight * confidence_proxy
            #       + difficulty_weight * difficulty_score
            values = np.array(
                [
                    suggestion.expectedImpact,
                    0.8,
                    difficulty_score,
                ]
            )

            weight_vector = np.array(
                [
                    weights["impact"],
                    weights["confidence"],
                    weights["difficulty"],
                ]
            )

            score = float(np.dot(values, weight_vector))

            ranked.append(
                RankedSuggestion(
                    suggestionType=suggestion.suggestionType,
                    action=suggestion.action,
                    field=suggestion.field,
                    currentValue=suggestion.currentValue,
                    suggestedValue=suggestion.suggestedValue,
                    expectedImpact=suggestion.expectedImpact,
                    difficulty=suggestion.difficulty,
                    description=suggestion.description,
                    score=round(score, 4),
                )
            )

        # Sort highest score first
        ranked.sort(key=lambda item: item.score, reverse=True)

        return ranked

    def _detect_patterns(
        self,
        missed_conditions: List[Any],
    ) -> Dict[str, Any]:
        # If no missed conditions exist, return empty pattern result
        if not missed_conditions:
            return {
                "mostCommonCondition": None,
                "conditionFrequency": {},
            }

        # Convert missed conditions into a pandas DataFrame
        data = [
            {
                "condition": condition.condition,
                "impact": condition.impact,
                "confidence": condition.confidence,
            }
            for condition in missed_conditions
        ]

        df = pd.DataFrame(data)

        # Count how often each condition appears
        frequency = df["condition"].value_counts().to_dict()

        # Find most common condition
        most_common = df["condition"].value_counts().idxmax()

        # Calculate average impact
        average_impact = float(df["impact"].mean())

        return {
            "mostCommonCondition": most_common,
            "conditionFrequency": frequency,
            "averageImpact": round(average_impact, 4),
        }

    def _select_algorithm(
        self,
        current_result: RuleEngineResult,
    ) -> str:
        # Very simple custom A/B testing framework for Phase 1
        # Later this can route traffic between heuristic, decision tree, or trained models

        default_algorithm = self.config["ab_testing"]["default_algorithm"]

        amount = current_result.transaction.get("amount", 0)

        # Example A/B rule:
        # large transactions can use decision-tree-assisted analysis
        if amount >= 1000:
            return "decision_tree"

        return default_algorithm

    def register_plugin(
        self,
        name: str,
        plugin: Any,
    ) -> None:
        # Register future ML algorithm plugin
        self.plugins[name] = plugin

    def analyze_portfolio(
            self,
            analyses: List[Any],
    ) -> PortfolioPatternResponse:
        rows = []

        for item in analyses:
            analysis = item.analysis if hasattr(item, "analysis") else item

            for condition in analysis.missedConditions:
                rows.append(
                    {
                        "condition": condition.condition,
                        "impact": condition.impact,
                    }
                )

        if not rows:
            return PortfolioPatternResponse(
                mostCommonCondition=None,
                highestImpactCondition=None,
                conditionFrequency={},
                averageImpactByCondition={},
                totalSavingsOpportunity={},
            )

        df = pd.DataFrame(rows)

        frequency = df["condition"].value_counts().to_dict()

        average_impact = (
            df.groupby("condition")["impact"]
            .mean()
            .round(4)
            .to_dict()
        )

        total_savings = (
            df.groupby("condition")["impact"]
            .sum()
            .round(4)
            .to_dict()
        )

        most_common_condition = df["condition"].value_counts().idxmax()

        highest_impact_condition = (
            df.groupby("condition")["impact"]
            .sum()
            .idxmax()
        )

        return PortfolioPatternResponse(
            mostCommonCondition=most_common_condition,
            highestImpactCondition=highest_impact_condition,
            conditionFrequency=frequency,
            averageImpactByCondition=average_impact,
            totalSavingsOpportunity=total_savings,
        )

    def detect_anomalies(
            self,
            results: List[RuleEngineResult],
    ) -> AnomalyDetectionResponse:
        """
        Detect abnormal transactions across a transaction portfolio.

        This version does NOT rely on __init__.
        It creates the AnomalyDetector on demand.

        Pros:
        - No need to modify constructor
        - Cleaner for optional/feature-based components

        Cons:
        - Slight overhead (negligible for this use case)
        """

        # Instantiate detector locally (instead of using self.anomaly_detector)
        detector = AnomalyDetector()

        # Delegate detection logic
        return detector.detect(results)

    def simulate_bulk_scenarios(
            self,
            request: BulkSimulationRequest,
    ) -> BulkSimulationResponse:
        """
        Simulate recommendation impact across multiple transactions.

        For each transaction:
        - Run the existing ML analysis pipeline
        - Select the top N ranked recommendations
        - Apply those recommendations through the simulator
        - Estimate the financial impact
        """

        total_current_fees = 0.0
        total_simulated_fees = 0.0
        savings_by_condition = {}
        skipped_transactions = []
        processed_transactions = 0

        # Prevent negative recommendation limits
        top_n = max(request.applyTopNRecommendations, 0)

        for index, item in enumerate(request.transactions):
            try:
                current_result = item.currentResult
                optimal_result = item.optimalResult

                # Run existing pipeline:
                # missed conditions -> suggestions -> ranking -> simulation
                analysis_result = self.analyze_transaction(
                    current_result,
                    optimal_result,
                )

                # Only apply the top N recommendations requested by the user
                selected_suggestions = analysis_result.rankedSuggestions[:top_n]

                # If no suggestions should be applied, simulated fee remains current fee
                if not selected_suggestions:
                    total_current_fees += current_result.feeAmount
                    total_simulated_fees += current_result.feeAmount
                    processed_transactions += 1
                    continue

                # Use the existing simulator so validation rules are respected
                simulation = self.simulator.simulate(
                    current_result.transaction,
                    selected_suggestions,
                )

                # Invalid simulated transactions are excluded and logged
                if not simulation.valid:
                    skipped_transactions.append(
                        BulkSimulationSkippedTransaction(
                            index=index,
                            reason=", ".join(simulation.validationMessages),
                        )
                    )
                    continue

                current_fee = current_result.feeAmount
                optimal_fee = optimal_result.feeAmount

                # Estimate savings proportionally to the selected recommendations
                total_available_impact = sum(
                    suggestion.expectedImpact
                    for suggestion in analysis_result.rankedSuggestions
                )

                selected_impact = sum(
                    suggestion.expectedImpact
                    for suggestion in selected_suggestions
                )

                if total_available_impact <= 0:
                    estimated_savings = 0.0
                else:
                    full_possible_savings = max(current_fee - optimal_fee, 0)
                    estimated_savings = full_possible_savings * (
                            selected_impact / total_available_impact
                    )

                simulated_fee = current_fee - estimated_savings

                total_current_fees += current_fee
                total_simulated_fees += simulated_fee
                processed_transactions += 1

                # Group savings by suggestion type
                for suggestion in selected_suggestions:
                    if total_available_impact <= 0:
                        condition_savings = 0.0
                    else:
                        condition_savings = estimated_savings * (
                                suggestion.expectedImpact / selected_impact
                        )

                    current_value = savings_by_condition.get(
                        suggestion.suggestionType,
                        0.0,
                    )

                    savings_by_condition[suggestion.suggestionType] = (
                            current_value + condition_savings
                    )

            except Exception as error:
                # Keep processing remaining transactions even if one item fails
                skipped_transactions.append(
                    BulkSimulationSkippedTransaction(
                        index=index,
                        reason=str(error),
                    )
                )

        total_current_fees = round(total_current_fees, 4)
        total_simulated_fees = round(total_simulated_fees, 4)
        total_savings = round(total_current_fees - total_simulated_fees, 4)

        rounded_savings_by_condition = {
            key: round(value, 4)
            for key, value in savings_by_condition.items()
        }

        return BulkSimulationResponse(
            totalCurrentFees=total_current_fees,
            totalSimulatedFees=total_simulated_fees,
            totalSavings=total_savings,
            savingsByCondition=rounded_savings_by_condition,
            processedTransactions=processed_transactions,
            skippedTransactions=skipped_transactions,
        )

    def analyze_root_causes(
            self,
            analyses: List[Any],
    ) -> RootCauseAnalysisResponse:
        """
        Identify systemic optimization drivers across a portfolio.

        The analyzer is created only when this method is called.
        """

        analyzer = RootCauseAnalyzer()

        return analyzer.analyze(analyses)

    def _get_model_registry(self) -> ModelRegistry:
        """
        Lazy-load the model registry.

        This avoids modifying __init__ and keeps Story 4.11 optional.
        The registry is in-memory for now and can later be backed by files,
        database records, or MLflow.
        """

        if not hasattr(self, "_model_registry"):
            self._model_registry = ModelRegistry()

            # Register placeholder metadata for Phase 2 models.
            # The artifacts may not exist yet, so loading will safely fallback.
            self._model_registry.register_model(
                ModelMetadata(
                    name="impact_prediction",
                    version="impact-model-v1",
                    trainedDate="2026-05-05",
                    featureSchema=[
                        "amount",
                        "feeRate",
                        "feeAmount",
                        "category",
                        "threeDS",
                        "clearingDelayDays",
                    ],
                    metrics={},
                    artifactPath="models/artifacts/impact-model-v1.joblib",
                )
            )

            self._model_registry.register_model(
                ModelMetadata(
                    name="recommendation_ranking",
                    version="ranking-model-v1",
                    trainedDate="2026-05-05",
                    featureSchema=[
                        "amount",
                        "expectedImpact",
                        "difficulty",
                        "condition",
                    ],
                    metrics={},
                    artifactPath="models/artifacts/ranking-model-v1.joblib",
                )
            )

            self._model_registry.register_model(
                ModelMetadata(
                    name="anomaly_detection",
                    version="anomaly-model-v1",
                    trainedDate="2026-05-05",
                    featureSchema=[
                        "amount",
                        "feeRate",
                        "feeAmount",
                        "category",
                        "clearingDelayDays",
                    ],
                    metrics={},
                    artifactPath="models/artifacts/anomaly-model-v1.joblib",
                )
            )

            self._model_registry.register_model(
                ModelMetadata(
                    name="root_cause_driver",
                    version="root-cause-model-v1",
                    trainedDate="2026-05-05",
                    featureSchema=[
                        "condition",
                        "frequency",
                        "averageImpact",
                        "totalImpact",
                    ],
                    metrics={},
                    artifactPath="models/artifacts/root-cause-model-v1.joblib",
                )
            )

        return self._model_registry

    def load_active_model(
        self,
        model_key: str,
        available_features: List[str],
    ):
        """
        Load an active model from config.

        If the configured model is missing, invalid, or incompatible,
        this method returns a safe fallback result instead of crashing MLCore.
        """

        active_models = self.config.get("active_models", {})
        model_version = active_models.get(model_key)

        if model_version is None:
            registry = self._get_model_registry()

            return registry.load_model(
                version="__missing__",
                available_features=available_features,
            )

        registry = self._get_model_registry()

        return registry.load_model(
            version=model_version,
            available_features=available_features,
        )

    def _get_impact_prediction_model(self) -> ImpactPredictionModel:
        """
        Lazy-load impact prediction model.

        This avoids modifying __init__ and only creates the model when needed.
        """

        if not hasattr(self, "_impact_prediction_model"):
            model_config = self.config.get("models", {}).get("impact_prediction", {})

            self._impact_prediction_model = ImpactPredictionModel(
                model_version="impact-model-v1",
                confidence_threshold=model_config.get("confidence_threshold", 0.65),
                min_training_records=model_config.get("min_training_records", 20),
                random_state=model_config.get("random_state", 42),
            )

            artifact_path = model_config.get(
                "artifact_path",
                "models/artifacts/impact-model-v1.joblib",
            )

            try:
                self._impact_prediction_model.load(artifact_path)
            except Exception:
                # Missing model artifact is allowed.
                # Prediction will safely fallback to heuristic.
                pass

        return self._impact_prediction_model

    def predict_impact(
        self,
        features: Dict[str, Any],
        heuristic_impact: float,
    ):
        """
        Predict missed-condition impact.

        Uses ML model when enabled and available.
        Falls back to heuristic impact otherwise.
        """

        model_config = self.config.get("models", {}).get("impact_prediction", {})

        if not model_config.get("enabled", False):
            return {
                "predictedImpact": heuristic_impact,
                "modelConfidence": 0.0,
                "modelVersion": None,
                "fallbackUsed": True,
                "warnings": ["Impact prediction model disabled."],
            }

        model = self._get_impact_prediction_model()

        result = model.predict(
            features=features,
            heuristic_impact=heuristic_impact,
        )

        return result.model_dump()