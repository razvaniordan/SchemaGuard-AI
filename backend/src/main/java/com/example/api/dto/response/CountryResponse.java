package com.example.api.dto.response;

public record CountryResponse(
        String countryCode,
        String countryName,
        String regionCode,
        String regionName
) {}
