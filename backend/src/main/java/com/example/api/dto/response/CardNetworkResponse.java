package com.example.api.dto.response;

public record CardNetworkResponse(
        Long cardNetworkId,
        String networkCode,
        String networkName
) {}
