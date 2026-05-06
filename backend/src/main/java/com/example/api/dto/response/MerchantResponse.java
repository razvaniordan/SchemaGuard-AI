package com.example.api.dto.response;

public record MerchantResponse(
        Long merchantId,
        String merchantName,
        String mccCode,
        String mccDescription,
        String countryCode,
        String countryName,
        String city,
        String address,
        Long acquiringPartnerId,
        String acquiringPartnerName
) {}
