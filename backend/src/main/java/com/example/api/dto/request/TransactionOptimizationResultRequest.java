package com.example.api.dto.request;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

public record TransactionOptimizationResultRequest(
        @NotNull Long transactionId,
        @NotNull Long currentResultId,
        @NotNull Long optimalResultId,
        @NotNull @DecimalMin("0.00") BigDecimal currentFeeAmount,
        @NotNull @DecimalMin("0.00") BigDecimal optimalFeeAmount,
        @NotNull @DecimalMin("0.00") BigDecimal savingAmount,
        @DecimalMin("0.0000") BigDecimal savingPercentage
) {}
