package com.example.api.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record MccCodeRequest(
        @NotBlank @Pattern(regexp = "^[0-9]{4}$") String mccCode,
        @NotBlank @Size(max = 255) String mccDescription
) {}
