package com.example.api.controller;

import com.example.api.dto.request.InterchangeRuleRequest;
import com.example.api.dto.response.InterchangeRuleResponse;
import com.example.api.service.InterchangeRuleService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/interchange-rules")
@Tag(name = "InterchangeRule")
@SecurityRequirement(name = "bearerAuth")
public class InterchangeRuleController {
    private final InterchangeRuleService interchangeRuleService;

    public InterchangeRuleController(InterchangeRuleService interchangeRuleService) {
        this.interchangeRuleService = interchangeRuleService;
    }

    @GetMapping
    @Operation(summary = "List interchange-rules")
    public List<InterchangeRuleResponse> findAll() {
        return interchangeRuleService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create interchange-rule")
    public InterchangeRuleResponse create(@Valid @RequestBody InterchangeRuleRequest request) {
        return interchangeRuleService.create(request);
    }
}
