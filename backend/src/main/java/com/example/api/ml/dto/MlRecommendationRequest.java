package com.example.api.ml.dto;

public record MlRecommendationRequest(
        MlRuleEngineResult currentResult,
        MlRuleEngineResult optimalResult
) {}