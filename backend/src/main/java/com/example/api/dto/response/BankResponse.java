package com.example.api.dto.response;

public record BankResponse(
        Long bankId,
        String bankName,
        String countryCode,
        String countryName
) {}
