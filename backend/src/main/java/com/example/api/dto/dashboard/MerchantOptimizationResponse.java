package com.example.api.dto.dashboard;

import java.math.BigDecimal;

public record MerchantOptimizationResponse(
        long merchantKey,
        long sourceMerchantId,
        String merchantName,
        String mccCode,
        String mccDescription,
        long transactionCount,
        BigDecimal totalTransactionAmount,
        BigDecimal totalCurrentFeeAmount,
        BigDecimal totalOptimalFeeAmount,
        BigDecimal totalSavingAmount,
        BigDecimal avgSavingPercentage
) {
}
