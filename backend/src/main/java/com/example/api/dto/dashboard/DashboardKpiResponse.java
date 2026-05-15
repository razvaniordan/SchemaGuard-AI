package com.example.api.dto.dashboard;

import java.math.BigDecimal;

public record DashboardKpiResponse(
        long transactionCount,
        BigDecimal totalTransactionAmount,
        BigDecimal totalCurrentFeeAmount,
        BigDecimal totalOptimalFeeAmount,
        BigDecimal totalSavingAmount,
        BigDecimal avgSavingPercentage
) {
}
