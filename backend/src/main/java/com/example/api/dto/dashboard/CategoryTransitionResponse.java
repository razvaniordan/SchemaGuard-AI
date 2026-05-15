package com.example.api.dto.dashboard;

import java.math.BigDecimal;

public record CategoryTransitionResponse(
        long currentCategoryKey,
        String currentCategoryName,
        long optimalCategoryKey,
        String optimalCategoryName,
        long transactionCount,
        BigDecimal totalCurrentFeeAmount,
        BigDecimal totalOptimalFeeAmount,
        BigDecimal totalSavingAmount,
        BigDecimal avgSavingPercentage
) {
}
