package com.example.api.service;

import com.example.api.dto.request.CountryRequest;
import com.example.api.dto.response.CountryResponse;
import com.example.api.entity.Country;
import com.example.api.entity.Region;
import com.example.api.repository.CountryRepository;
import com.example.api.repository.RegionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CountryService {
    private final CountryRepository countryRepository;
    private final RegionRepository regionRepository;

    public CountryService(CountryRepository countryRepository, RegionRepository regionRepository) {
        this.countryRepository = countryRepository;
        this.regionRepository = regionRepository;
    }

    @Transactional(readOnly = true)
    public List<CountryResponse> findAll() {
        return countryRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public CountryResponse create(CountryRequest request) {
        Region region = regionRepository.findById(request.regionCode())
                .orElseThrow(() -> new IllegalArgumentException("Region not found: " + request.regionCode()));
        Country country = Country.builder()
                .countryCode(request.countryCode())
                .countryName(request.countryName())
                .region(region)
                .build();
        return toResponse(countryRepository.save(country));
    }

    private CountryResponse toResponse(Country country) {
        return new CountryResponse(
                country.getCountryCode(),
                country.getCountryName(),
                country.getRegion().getRegionCode(),
                country.getRegion().getRegionName()
        );
    }
}
