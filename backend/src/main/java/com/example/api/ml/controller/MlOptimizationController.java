package com.example.api.ml.controller;

import com.example.api.ml.service.MlOptimizationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ml/transactions")
@RequiredArgsConstructor
public class MlOptimizationController {

    private final MlOptimizationService mlOptimizationService;

    /**
     * Compares current transaction fees against an optimized scenario.
     *
     * Example:
     * GET /api/ml/transactions/1/fee-comparison?monthlyVolume=1000&yearlyVolume=12000
     */
    @GetMapping("/{transactionId}/fee-comparison")
    public String compareFees(
            @PathVariable Long transactionId,
            @RequestParam(required = false) Integer monthlyVolume,
            @RequestParam(required = false) Integer yearlyVolume
    ) {
        return mlOptimizationService.compareFees(
                transactionId,
                monthlyVolume,
                yearlyVolume
        );
    }
}