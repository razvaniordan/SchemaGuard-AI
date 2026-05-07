package com.example.api.dto.response;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record TransactionOptimizationResultResponse(
        Long optimizationResultId,
        Long transactionId,
        Long currentResultId,
        Long optimalResultId,
        BigDecimal currentFeeAmount,
        BigDecimal optimalFeeAmount,
        BigDecimal savingAmount,
        BigDecimal savingPercentage,
        LocalDateTime createdAt
) {}
