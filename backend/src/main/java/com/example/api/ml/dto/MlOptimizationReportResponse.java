package com.example.api.ml.dto;

import com.fasterxml.jackson.databind.JsonNode;

public record MlOptimizationReportResponse(
        Long transactionId,
        String summary,
        JsonNode feeComparison,
        JsonNode savingsProjections,
        JsonNode missedConditions,
        JsonNode rankedRecommendations,
        JsonNode anomalyInsights
) {}