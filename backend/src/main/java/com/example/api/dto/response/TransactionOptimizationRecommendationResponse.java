package com.example.api.dto.response;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record TransactionOptimizationRecommendationResponse(
        Long recommendationId,
        Long transactionId,
        String recommendationType,
        String recommendationText,
        String currentValue,
        String recommendedValue,
        String impactDescription,
        BigDecimal estimatedSavingAmount,
        BigDecimal estimatedSavingPercentage,
        Long priorityRank,
        LocalDateTime createdAt
) {}
