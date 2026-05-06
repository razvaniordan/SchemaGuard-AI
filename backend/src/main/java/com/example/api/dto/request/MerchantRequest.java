package com.example.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record MerchantRequest(
        @NotBlank @Size(max = 150) String merchantName,
        @NotBlank String mccCode,
        @NotBlank String countryCode,
        @NotBlank @Size(max = 100) String city,
        @NotBlank @Size(max = 255) String address,
        @NotNull Long acquiringPartnerId
) {}
