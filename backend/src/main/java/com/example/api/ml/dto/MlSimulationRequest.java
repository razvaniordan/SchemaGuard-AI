package com.example.api.ml.dto;

import java.util.List;

public record MlSimulationRequest(

        // Canonical flattened transaction used by ML Core
        PythonTransactionInput transaction,

        // Optimization suggestions to simulate
        List<MlRecommendationSuggestion> suggestions

) {}