package com.example.api.dto.response;

public record ClientResponse(
        Long clientId,
        String clientName,
        String countryCode,
        String countryName
) {}