package com.example.api.dto.request;

import jakarta.validation.constraints.*;

import java.math.BigDecimal;

public record TransactionOptimizationRecommendationRequest(
        @NotNull Long transactionId,
        @NotBlank @Size(max = 50) String recommendationType,
        @NotBlank @Size(max = 500) String recommendationText,
        @Size(max = 100) String currentValue,
        @Size(max = 100) String recommendedValue,
        @Size(max = 500) String impactDescription,
        @DecimalMin("0.00") BigDecimal estimatedSavingAmount,
        @DecimalMin("0.0000") BigDecimal estimatedSavingPercentage,
        @NotNull @Min(1) Integer priorityRank
) {}
