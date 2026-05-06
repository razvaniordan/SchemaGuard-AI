package com.example.api.controller;

import com.example.api.dto.request.TransactionSimulationRequest;
import com.example.api.dto.response.TransactionSimulationResponse;
import com.example.api.service.TransactionSimulationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/transaction-simulations")
@Tag(name = "TransactionSimulation")
@SecurityRequirement(name = "bearerAuth")
public class TransactionSimulationController {
    private final TransactionSimulationService transactionSimulationService;

    public TransactionSimulationController(TransactionSimulationService transactionSimulationService) {
        this.transactionSimulationService = transactionSimulationService;
    }

    @GetMapping
    @Operation(summary = "List transaction-simulations")
    public List<TransactionSimulationResponse> findAll() {
        return transactionSimulationService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create transaction-simulation")
    public TransactionSimulationResponse create(@Valid @RequestBody TransactionSimulationRequest request) {
        return transactionSimulationService.create(request);
    }
}
