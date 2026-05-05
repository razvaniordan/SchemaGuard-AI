package com.example.api.dto.request;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;

public record TransactionSimulationRequest(
        @NotNull Long transactionId,
        @Pattern(regexp = "^[YN]$") String simulatedIs3dsAuthenticated,
        @Size(max = 2) String simulatedEciValue,
        LocalDateTime simulatedClearingDatetime,
        String simulatedRegionCode,
        @Size(max = 500) String simulationReason
) {}
