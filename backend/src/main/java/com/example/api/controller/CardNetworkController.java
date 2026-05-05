package com.example.api.controller;

import com.example.api.dto.request.CardNetworkRequest;
import com.example.api.dto.response.CardNetworkResponse;
import com.example.api.service.CardNetworkService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/card-networks")
@Tag(name = "CardNetwork")
@SecurityRequirement(name = "bearerAuth")
public class CardNetworkController {
    private final CardNetworkService cardNetworkService;

    public CardNetworkController(CardNetworkService cardNetworkService) {
        this.cardNetworkService = cardNetworkService;
    }

    @GetMapping
    @Operation(summary = "List card-networks")
    public List<CardNetworkResponse> findAll() {
        return cardNetworkService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create card-network")
    public CardNetworkResponse create(@Valid @RequestBody CardNetworkRequest request) {
        return cardNetworkService.create(request);
    }
}
