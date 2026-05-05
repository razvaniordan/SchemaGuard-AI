package com.example.api.dto.response;

public record InterchangeCategoryResponse(
        Long categoryId,
        String categoryName,
        String description
) {}
