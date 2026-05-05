package com.example.api.controller;

import com.example.api.dto.request.InterchangeCategoryRequest;
import com.example.api.dto.response.InterchangeCategoryResponse;
import com.example.api.service.InterchangeCategoryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/interchange-categories")
@Tag(name = "InterchangeCategory")
@SecurityRequirement(name = "bearerAuth")
public class InterchangeCategoryController {
    private final InterchangeCategoryService interchangeCategoryService;

    public InterchangeCategoryController(InterchangeCategoryService interchangeCategoryService) {
        this.interchangeCategoryService = interchangeCategoryService;
    }

    @GetMapping
    @Operation(summary = "List interchange-categories")
    public List<InterchangeCategoryResponse> findAll() {
        return interchangeCategoryService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create interchange-categorie")
    public InterchangeCategoryResponse create(@Valid @RequestBody InterchangeCategoryRequest request) {
        return interchangeCategoryService.create(request);
    }
}
