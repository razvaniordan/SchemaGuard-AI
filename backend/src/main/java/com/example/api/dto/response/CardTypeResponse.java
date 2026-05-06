package com.example.api.dto.response;

public record CardTypeResponse(
        Long cardTypeId,
        String cardTypeName,
        String description
) {}
