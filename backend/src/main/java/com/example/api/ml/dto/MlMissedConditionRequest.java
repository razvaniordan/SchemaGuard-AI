package com.example.api.ml.dto;

public record MlMissedConditionRequest(
        MlRuleEngineResult currentResult,
        MlRuleEngineResult optimalResult
) {}