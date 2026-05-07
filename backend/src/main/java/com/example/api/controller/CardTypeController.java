package com.example.api.controller;

import com.example.api.dto.request.CardTypeRequest;
import com.example.api.dto.response.CardTypeResponse;
import com.example.api.service.CardTypeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/card-types")
@Tag(name = "CardType")
@SecurityRequirement(name = "bearerAuth")
public class CardTypeController {
    private final CardTypeService cardTypeService;

    public CardTypeController(CardTypeService cardTypeService) {
        this.cardTypeService = cardTypeService;
    }

    @GetMapping
    @Operation(summary = "List card-types")
    public List<CardTypeResponse> findAll() {
        return cardTypeService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create card-type")
    public CardTypeResponse create(@Valid @RequestBody CardTypeRequest request) {
        return cardTypeService.create(request);
    }
}
