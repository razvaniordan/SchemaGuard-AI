package com.example.api.dto.response;

import com.example.api.entity.AcquiringPartner.PartnerType;

public record AcquiringPartnerResponse(
        Long acquiringPartnerId,
        String partnerName,
        PartnerType partnerType,
        String countryCode,
        String countryName
) {}
