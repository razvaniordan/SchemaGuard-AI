package com.example.api.service;

import com.example.api.dto.request.RegionRequest;
import com.example.api.dto.response.RegionResponse;
import com.example.api.entity.Region;
import com.example.api.repository.RegionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class RegionService {
    private final RegionRepository regionRepository;

    public RegionService(RegionRepository regionRepository) {
        this.regionRepository = regionRepository;
    }

    @Transactional(readOnly = true)
    public List<RegionResponse> findAll() {
        return regionRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public RegionResponse create(RegionRequest request) {
        Region region = Region.builder()
                .regionCode(request.regionCode())
                .regionName(request.regionName())
                .description(request.description())
                .build();
        return toResponse(regionRepository.save(region));
    }

    private RegionResponse toResponse(Region region) {
        return new RegionResponse(region.getRegionCode(), region.getRegionName(), region.getDescription());
    }
}
