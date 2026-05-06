package com.example.api.service;

import com.example.api.dto.request.MerchantRequest;
import com.example.api.dto.response.MerchantResponse;
import com.example.api.entity.*;
import com.example.api.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class MerchantService {
    private final MerchantRepository merchantRepository;
    private final MccCodeRepository mccCodeRepository;
    private final CountryRepository countryRepository;
    private final AcquiringPartnerRepository acquiringPartnerRepository;

    public MerchantService(MerchantRepository merchantRepository, MccCodeRepository mccCodeRepository,
                           CountryRepository countryRepository, AcquiringPartnerRepository acquiringPartnerRepository) {
        this.merchantRepository = merchantRepository;
        this.mccCodeRepository = mccCodeRepository;
        this.countryRepository = countryRepository;
        this.acquiringPartnerRepository = acquiringPartnerRepository;
    }

    @Transactional(readOnly = true)
    public List<MerchantResponse> findAll() {
        return merchantRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public MerchantResponse create(MerchantRequest request) {
        MccCode mcc = mccCodeRepository.findById(request.mccCode())
                .orElseThrow(() -> new IllegalArgumentException("MCC not found: " + request.mccCode()));
        Country country = countryRepository.findById(request.countryCode())
                .orElseThrow(() -> new IllegalArgumentException("Country not found: " + request.countryCode()));
        AcquiringPartner acquiringPartner = acquiringPartnerRepository.findById(request.acquiringPartnerId())
                .orElseThrow(() -> new IllegalArgumentException("Acquiring partner not found: " + request.acquiringPartnerId()));

        Merchant merchant = Merchant.builder()
                .merchantName(request.merchantName())
                .mcc(mcc)
                .country(country)
                .city(request.city())
                .address(request.address())
                .acquiringPartner(acquiringPartner)
                .build();
        return toResponse(merchantRepository.save(merchant));
    }

    private MerchantResponse toResponse(Merchant merchant) {
        return new MerchantResponse(
                merchant.getMerchantId(),
                merchant.getMerchantName(),
                merchant.getMcc().getMccCode(),
                merchant.getMcc().getMccDescription(),
                merchant.getCountry().getCountryCode(),
                merchant.getCountry().getCountryName(),
                merchant.getCity(),
                merchant.getAddress(),
                merchant.getAcquiringPartner().getAcquiringPartnerId(),
                merchant.getAcquiringPartner().getPartnerName()
        );
    }
}
