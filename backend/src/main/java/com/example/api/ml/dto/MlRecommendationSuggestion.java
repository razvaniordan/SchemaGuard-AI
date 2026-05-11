package com.example.api.ml.dto;

public record MlRecommendationSuggestion(
        String suggestionType,
        String action,
        String field,
        Object currentValue,
        Object suggestedValue,
        Double expectedImpact,
        String difficulty,
        String description,
        Double score,
        String priority,
        String rankingReason
) {}