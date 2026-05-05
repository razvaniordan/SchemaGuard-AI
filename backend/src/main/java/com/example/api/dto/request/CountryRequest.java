package com.example.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record CountryRequest(
        @NotBlank @Pattern(regexp = "^[A-Z]{2}$") String countryCode,
        @NotBlank @Size(max = 100) String countryName,
        @NotBlank String regionCode
) {}
