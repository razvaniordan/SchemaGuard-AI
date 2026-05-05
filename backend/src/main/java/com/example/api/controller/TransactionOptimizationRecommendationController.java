package com.example.api.controller;

import com.example.api.dto.request.TransactionOptimizationRecommendationRequest;
import com.example.api.dto.response.TransactionOptimizationRecommendationResponse;
import com.example.api.service.TransactionOptimizationRecommendationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/transaction-optimization-recommendations")
@Tag(name = "TransactionOptimizationRecommendation")
@SecurityRequirement(name = "bearerAuth")
public class TransactionOptimizationRecommendationController {
    private final TransactionOptimizationRecommendationService transactionOptimizationRecommendationService;

    public TransactionOptimizationRecommendationController(TransactionOptimizationRecommendationService transactionOptimizationRecommendationService) {
        this.transactionOptimizationRecommendationService = transactionOptimizationRecommendationService;
    }

    @GetMapping
    @Operation(summary = "List transaction-optimization-recommendations")
    public List<TransactionOptimizationRecommendationResponse> findAll() {
        return transactionOptimizationRecommendationService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create transaction-optimization-recommendation")
    public TransactionOptimizationRecommendationResponse create(@Valid @RequestBody TransactionOptimizationRecommendationRequest request) {
        return transactionOptimizationRecommendationService.create(request);
    }
}
