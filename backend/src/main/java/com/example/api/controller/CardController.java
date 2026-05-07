package com.example.api.controller;

import com.example.api.dto.request.CardRequest;
import com.example.api.dto.response.CardResponse;
import com.example.api.service.CardService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cards")
@Tag(name = "Card")
@SecurityRequirement(name = "bearerAuth")
public class CardController {
    private final CardService cardService;

    public CardController(CardService cardService) {
        this.cardService = cardService;
    }

    @GetMapping
    @Operation(summary = "List cards")
    public List<CardResponse> findAll() {
        return cardService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create card")
    public CardResponse create(@Valid @RequestBody CardRequest request) {
        return cardService.create(request);
    }
}
