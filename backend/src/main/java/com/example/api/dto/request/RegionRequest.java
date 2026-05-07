package com.example.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record RegionRequest(
        @NotBlank @Size(max = 30) String regionCode,
        @NotBlank @Size(max = 100) String regionName,
        @Size(max = 255) String description
) {}
