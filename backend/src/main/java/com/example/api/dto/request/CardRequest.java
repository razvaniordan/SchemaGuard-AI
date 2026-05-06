package com.example.api.dto.request;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record CardRequest(
        @NotNull Long clientId,
        @NotNull Long issuerBankId,
        @NotNull Long cardNetworkId,
        @NotNull Long cardTypeId,
        @Size(max = 30) String cardProductType
) {}
