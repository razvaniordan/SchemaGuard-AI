package com.example.api.dto.response;

public record CardResponse(
        Long cardId,
        Long clientId,
        String clientName,
        Long issuerBankId,
        String issuerBankName,
        Long cardNetworkId,
        String networkName,
        Long cardTypeId,
        String cardTypeName,
        String cardProductType
) {}
