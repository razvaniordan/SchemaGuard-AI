package com.example.api.service;

import com.example.api.dto.request.AcquiringPartnerRequest;
import com.example.api.dto.response.AcquiringPartnerResponse;
import com.example.api.entity.AcquiringPartner;
import com.example.api.entity.Country;
import com.example.api.repository.AcquiringPartnerRepository;
import com.example.api.repository.CountryRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class AcquiringPartnerService {
    private final AcquiringPartnerRepository acquiringPartnerRepository;
    private final CountryRepository countryRepository;

    public AcquiringPartnerService(AcquiringPartnerRepository acquiringPartnerRepository, CountryRepository countryRepository) {
        this.acquiringPartnerRepository = acquiringPartnerRepository;
        this.countryRepository = countryRepository;
    }

    @Transactional(readOnly = true)
    public List<AcquiringPartnerResponse> findAll() {
        return acquiringPartnerRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public AcquiringPartnerResponse create(AcquiringPartnerRequest request) {
        Country country = countryRepository.findById(request.countryCode())
                .orElseThrow(() -> new IllegalArgumentException("Country not found: " + request.countryCode()));
        AcquiringPartner acquiringPartner = AcquiringPartner.builder()
                .partnerName(request.partnerName())
                .partnerType(request.partnerType())
                .country(country)
                .build();
        return toResponse(acquiringPartnerRepository.save(acquiringPartner));
    }

    private AcquiringPartnerResponse toResponse(AcquiringPartner acquiringPartner) {
        return new AcquiringPartnerResponse(
                acquiringPartner.getAcquiringPartnerId(),
                acquiringPartner.getPartnerName(),
                acquiringPartner.getPartnerType(),
                acquiringPartner.getCountry().getCountryCode(),
                acquiringPartner.getCountry().getCountryName()
        );
    }
}
