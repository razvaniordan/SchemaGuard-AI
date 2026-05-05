package com.example.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CardNetworkRequest(
        @NotBlank @Size(max = 30) String networkCode,
        @NotBlank @Size(max = 100) String networkName
) {}
