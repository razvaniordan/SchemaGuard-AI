package com.example.api.ruleengine.model;

import java.math.BigDecimal;

public record RuleEngineResult(

        String category,

        Double feeRate,

        BigDecimal feeAmount,

        String appliedRuleCode,

        String appliedRuleName,

        String explanation

) {
}