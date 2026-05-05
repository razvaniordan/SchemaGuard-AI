package com.example.api.controller;

import com.example.api.dto.request.TransactionInterchangeResultRequest;
import com.example.api.dto.response.TransactionInterchangeResultResponse;
import com.example.api.service.TransactionInterchangeResultService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/transaction-interchange-results")
@Tag(name = "TransactionInterchangeResult")
@SecurityRequirement(name = "bearerAuth")
public class TransactionInterchangeResultController {
    private final TransactionInterchangeResultService transactionInterchangeResultService;

    public TransactionInterchangeResultController(TransactionInterchangeResultService transactionInterchangeResultService) {
        this.transactionInterchangeResultService = transactionInterchangeResultService;
    }

    @GetMapping
    @Operation(summary = "List transaction-interchange-results")
    public List<TransactionInterchangeResultResponse> findAll() {
        return transactionInterchangeResultService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create transaction-interchange-result")
    public TransactionInterchangeResultResponse create(@Valid @RequestBody TransactionInterchangeResultRequest request) {
        return transactionInterchangeResultService.create(request);
    }
}
