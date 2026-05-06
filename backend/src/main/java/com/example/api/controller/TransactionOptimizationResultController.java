package com.example.api.controller;

import com.example.api.dto.request.TransactionOptimizationResultRequest;
import com.example.api.dto.response.TransactionOptimizationResultResponse;
import com.example.api.service.TransactionOptimizationResultService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/transaction-optimization-results")
@Tag(name = "TransactionOptimizationResult")
@SecurityRequirement(name = "bearerAuth")
public class TransactionOptimizationResultController {
    private final TransactionOptimizationResultService transactionOptimizationResultService;

    public TransactionOptimizationResultController(TransactionOptimizationResultService transactionOptimizationResultService) {
        this.transactionOptimizationResultService = transactionOptimizationResultService;
    }

    @GetMapping
    @Operation(summary = "List transaction-optimization-results")
    public List<TransactionOptimizationResultResponse> findAll() {
        return transactionOptimizationResultService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create transaction-optimization-result")
    public TransactionOptimizationResultResponse create(@Valid @RequestBody TransactionOptimizationResultRequest request) {
        return transactionOptimizationResultService.create(request);
    }
}
