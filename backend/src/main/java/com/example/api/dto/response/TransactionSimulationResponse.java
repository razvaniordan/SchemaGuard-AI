package com.example.api.dto.response;

import java.time.LocalDateTime;

public record TransactionSimulationResponse(
        Long simulationId,
        Long transactionId,
        String simulatedIs3dsAuthenticated,
        String simulatedEciValue,
        LocalDateTime simulatedClearingDatetime,
        String simulatedRegionCode,
        String simulatedRegionName,
        String simulationReason,
        LocalDateTime createdAt
) {}
