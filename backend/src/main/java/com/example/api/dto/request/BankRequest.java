package com.example.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record BankRequest(
        @NotBlank @Size(max = 100) String bankName,
        @NotBlank String countryCode
) {}
