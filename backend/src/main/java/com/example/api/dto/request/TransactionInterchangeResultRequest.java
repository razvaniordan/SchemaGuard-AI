package com.example.api.dto.request;

import com.example.api.entity.TransactionInterchangeResult.ResultType;
import jakarta.validation.constraints.*;

import java.math.BigDecimal;

public record TransactionInterchangeResultRequest(
        @NotNull Long transactionId,
        @NotNull ResultType resultType,
        @NotNull Long categoryId,
        Long appliedRuleId,
        @NotNull @DecimalMin("0.0000") BigDecimal feePercentage,
        @DecimalMin("0.00") BigDecimal fixedFeeAmount,
        @NotNull @DecimalMin("0.00") BigDecimal interchangeFeeAmount
) {}
