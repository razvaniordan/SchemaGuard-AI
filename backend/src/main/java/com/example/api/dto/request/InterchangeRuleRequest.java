package com.example.api.dto.request;

import com.example.api.entity.InterchangeRule.ClearingTimeCondition;
import com.example.api.entity.Transaction.TransactionChannel;
import jakarta.validation.constraints.*;

import java.math.BigDecimal;

public record InterchangeRuleRequest(
        @NotNull @Min(1) Integer rulePriority,
        Long cardNetworkId,
        String mccCode,
        Long cardTypeId,
        TransactionChannel transactionChannel,
        String regionCode,
        @Pattern(regexp = "^[YN]$") String is3dsRequired,
        ClearingTimeCondition clearingTimeCondition,
        @NotNull Long categoryId,
        @NotNull @DecimalMin("0.0000") BigDecimal feePercentage,
        @DecimalMin("0.00") BigDecimal fixedFeeAmount,
        @NotBlank @Size(min = 3, max = 3) String currencyCode
) {}
