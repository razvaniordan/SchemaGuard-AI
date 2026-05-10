package com.example.api.ml.dto;

public record MlFeeComparisonRequest(

        // Current rule-engine classification result
        MlRuleEngineResult currentResult,

        // Optimized/simulated rule-engine result
        MlRuleEngineResult optimalResult,

        // Optional business projection inputs
        Integer monthlyTransactionVolume,

        Integer yearlyTransactionVolume,

        // Reporting/display currency
        String currency

) {}