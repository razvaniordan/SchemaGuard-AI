package com.example.api.dto.response;

import com.example.api.entity.InterchangeRule.ClearingTimeCondition;
import com.example.api.entity.Transaction.TransactionChannel;

import java.math.BigDecimal;

public record InterchangeRuleResponse(
        Long ruleId,
        Long rulePriority,
        Long cardNetworkId,
        String networkName,
        String mccCode,
        String mccDescription,
        Long cardTypeId,
        String cardTypeName,
        TransactionChannel transactionChannel,
        String regionCode,
        String regionName,
        String is3dsRequired,
        ClearingTimeCondition clearingTimeCondition,
        Long categoryId,
        String categoryName,
        BigDecimal feePercentage,
        BigDecimal fixedFeeAmount,
        String currencyCode
) {}
