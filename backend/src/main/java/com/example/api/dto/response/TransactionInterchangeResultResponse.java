package com.example.api.dto.response;

import com.example.api.entity.TransactionInterchangeResult.ResultType;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record TransactionInterchangeResultResponse(
        Long resultId,
        Long transactionId,
        ResultType resultType,
        Long categoryId,
        String categoryName,
        Long appliedRuleId,
        BigDecimal feePercentage,
        BigDecimal fixedFeeAmount,
        BigDecimal interchangeFeeAmount,
        LocalDateTime evaluatedAt
) {}
