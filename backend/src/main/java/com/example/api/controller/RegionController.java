package com.example.api.controller;

import com.example.api.dto.request.RegionRequest;
import com.example.api.dto.response.RegionResponse;
import com.example.api.service.RegionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/regions")
@Tag(name = "Region")
@SecurityRequirement(name = "bearerAuth")
public class RegionController {
    private final RegionService regionService;

    public RegionController(RegionService regionService) {
        this.regionService = regionService;
    }

    @GetMapping
    @Operation(summary = "List regions")
    public List<RegionResponse> findAll() {
        return regionService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create region")
    public RegionResponse create(@Valid @RequestBody RegionRequest request) {
        return regionService.create(request);
    }
}
