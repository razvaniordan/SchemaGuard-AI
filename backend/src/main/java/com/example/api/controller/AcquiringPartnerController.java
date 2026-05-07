package com.example.api.controller;

import com.example.api.dto.request.AcquiringPartnerRequest;
import com.example.api.dto.response.AcquiringPartnerResponse;
import com.example.api.service.AcquiringPartnerService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/acquiring-partners")
@Tag(name = "AcquiringPartner")
@SecurityRequirement(name = "bearerAuth")
public class AcquiringPartnerController {
    private final AcquiringPartnerService acquiringPartnerService;

    public AcquiringPartnerController(AcquiringPartnerService acquiringPartnerService) {
        this.acquiringPartnerService = acquiringPartnerService;
    }

    @GetMapping
    @Operation(summary = "List acquiring-partners")
    public List<AcquiringPartnerResponse> findAll() {
        return acquiringPartnerService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create acquiring-partner")
    public AcquiringPartnerResponse create(@Valid @RequestBody AcquiringPartnerRequest request) {
        return acquiringPartnerService.create(request);
    }
}
