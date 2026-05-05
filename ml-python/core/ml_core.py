from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import yaml
from sklearn.tree import DecisionTreeClassifier

from core.missed_condition_detector import MissedConditionDetector
from core.change_suggestion_engine import ChangeSuggestionEngine
from core.transaction_simulator import TransactionSimulator
from models.analysis_models import (
    MLCoreResponse,
    RankedSuggestion,
    RuleEngineResult,
    PortfolioPatternResponse,
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
        return MLCoreResponse(
            analysis=analysis,
            rankedSuggestions=ranked_suggestions,
            simulation=simulation,
            detectedPatterns=detected_patterns,
            algorithmUsed=algorithm,
        )

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

