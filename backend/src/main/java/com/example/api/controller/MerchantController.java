package com.example.api.controller;

import com.example.api.dto.request.MerchantRequest;
import com.example.api.dto.response.MerchantResponse;
import com.example.api.service.MerchantService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/merchants")
@Tag(name = "Merchant")
@SecurityRequirement(name = "bearerAuth")
public class MerchantController {
    private final MerchantService merchantService;

    public MerchantController(MerchantService merchantService) {
        this.merchantService = merchantService;
    }

    @GetMapping
    @Operation(summary = "List merchants")
    public List<MerchantResponse> findAll() {
        return merchantService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create merchant")
    public MerchantResponse create(@Valid @RequestBody MerchantRequest request) {
        return merchantService.create(request);
    }
}
