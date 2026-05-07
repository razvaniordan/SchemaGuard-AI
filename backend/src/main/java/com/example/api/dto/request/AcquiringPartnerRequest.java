package com.example.api.dto.request;

import com.example.api.entity.AcquiringPartner.PartnerType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record AcquiringPartnerRequest(
        @NotBlank @Size(max = 100) String partnerName,
        @NotNull PartnerType partnerType,
        @NotBlank String countryCode
) {}
