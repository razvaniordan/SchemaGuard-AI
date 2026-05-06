package com.example.api.controller;

import com.example.api.dto.request.MccCodeRequest;
import com.example.api.dto.response.MccCodeResponse;
import com.example.api.service.MccCodeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/mcc-codes")
@Tag(name = "MCC Codes")
@SecurityRequirement(name = "bearerAuth")
public class MccCodeController {
    private final MccCodeService mccCodeService;

    public MccCodeController(MccCodeService mccCodeService) {
        this.mccCodeService = mccCodeService;
    }

    @GetMapping
    @Operation(summary = "List mcc-codes")
    public List<MccCodeResponse> findAll() {
        return mccCodeService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create mcc-code")
    public MccCodeResponse create(@Valid @RequestBody MccCodeRequest request) {
        return mccCodeService.create(request);
    }
}
