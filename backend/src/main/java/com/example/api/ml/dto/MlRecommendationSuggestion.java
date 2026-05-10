package com.example.api.ml.dto;

public record MlRecommendationSuggestion(

        // Transaction field to optimize
        String field,

        // Suggested value
        Object suggestedValue,

        // Recommendation type
        String suggestionType,

        // Human-readable action
        String action,

        // Business explanation
        String description,

        // Expected savings impact
        Double expectedImpact,

        // LOW / MEDIUM / HIGH
        String difficulty,

        // Confidence score
        Double confidence

) {}