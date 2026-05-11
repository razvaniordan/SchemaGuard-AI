package com.example.api.ml.dto;

import java.util.List;

public record MlSimulationRequest(
        PythonTransactionInput transaction,
        List<MlRecommendationSuggestion> suggestions
) {}