package com.example.api.controller;

import com.example.api.dto.request.CountryRequest;
import com.example.api.dto.response.CountryResponse;
import com.example.api.service.CountryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/countries")
@Tag(name = "Country")
@SecurityRequirement(name = "bearerAuth")
public class CountryController {
    private final CountryService countryService;

    public CountryController(CountryService countryService) {
        this.countryService = countryService;
    }

    @GetMapping
    @Operation(summary = "List countries")
    public List<CountryResponse> findAll() {
        return countryService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create countrie")
    public CountryResponse create(@Valid @RequestBody CountryRequest request) {
        return countryService.create(request);
    }
}
