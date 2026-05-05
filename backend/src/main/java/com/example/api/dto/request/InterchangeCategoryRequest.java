package com.example.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record InterchangeCategoryRequest(
        @NotBlank @Size(max = 100) String categoryName,
        @Size(max = 255) String description
) {}
