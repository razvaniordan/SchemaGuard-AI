package com.example.api.ml.dto;

public record MlRuleEngineResult(

        // Rule-engine category assigned to the transaction
        String category,

        // Fee rate stored as decimal fraction
        // Example: 0.0185 = 1.85%
        Double feeRate,

        // Final calculated fee amount
        Double feeAmount,

        // Canonical flattened transaction used by ML Core
        PythonTransactionInput transaction

) {}
