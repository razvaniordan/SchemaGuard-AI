package com.example.api.ml.dto;

public record MlMissedConditionRequest(

        // Current rule-engine result for the original transaction
        MlRuleEngineResult currentResult,

        // Optimized rule-engine result after simulation/recommendations
        MlRuleEngineResult optimalResult

) {}