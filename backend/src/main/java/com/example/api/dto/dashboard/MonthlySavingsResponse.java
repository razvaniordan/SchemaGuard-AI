package com.example.api.dto.dashboard;

import java.math.BigDecimal;

public record MonthlySavingsResponse(
        int yearNumber,
        int monthNumber,
        String monthName,
        long transactionCount,
        BigDecimal totalTransactionAmount,
        BigDecimal totalCurrentFeeAmount,
        BigDecimal totalOptimalFeeAmount,
        BigDecimal totalSavingAmount,
        BigDecimal avgSavingPercentage
) {
}
