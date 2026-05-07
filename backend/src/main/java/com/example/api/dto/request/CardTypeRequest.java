package com.example.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CardTypeRequest(
        @NotBlank @Size(max = 30) String cardTypeName,
        @Size(max = 255) String description
) {}
