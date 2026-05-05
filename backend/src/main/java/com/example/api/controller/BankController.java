package com.example.api.controller;

import com.example.api.dto.request.BankRequest;
import com.example.api.dto.response.BankResponse;
import com.example.api.service.BankService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/banks")
@Tag(name = "Bank")
@SecurityRequirement(name = "bearerAuth")
public class BankController {
    private final BankService bankService;

    public BankController(BankService bankService) {
        this.bankService = bankService;
    }

    @GetMapping
    @Operation(summary = "List banks")
    public List<BankResponse> findAll() {
        return bankService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create bank")
    public BankResponse create(@Valid @RequestBody BankRequest request) {
        return bankService.create(request);
    }
}
