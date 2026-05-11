package com.example.api.ml.controller;

import com.example.api.ml.dto.MlOptimizationReportResponse;
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
        System.out.println("HIT fee-comparison endpoint, transactionId=" + transactionId);
        return mlOptimizationService.compareFees(
                transactionId,
                monthlyVolume,
                yearlyVolume
        );
    }

    @GetMapping("/{transactionId}/recommendations")
    public String prioritizeRecommendations(@PathVariable Long transactionId) {
        System.out.println("HIT recommendations endpoint, transactionId=" + transactionId);
        return mlOptimizationService.prioritizeRecommendations(transactionId);
    }

    @GetMapping("/{transactionId}/simulation")
    public String simulateTransaction(@PathVariable Long transactionId) {
        System.out.println("HIT simulation endpoint, transactionId=" + transactionId);
        return mlOptimizationService.simulateTransaction(transactionId);
    }

    @GetMapping("/{transactionId}/missed-conditions")
    public String missedConditions(@PathVariable Long transactionId) {
        System.out.println("HIT missed-conditions endpoint, transactionId=" + transactionId);
        return mlOptimizationService.missedConditions(transactionId);
    }

    @GetMapping("/portfolio/anomalies")
    public String detectPortfolioAnomalies() {
        System.out.println("HIT portfolio anomalies endpoint");
        return mlOptimizationService.detectPortfolioAnomalies();
    }

    @GetMapping("/{transactionId}/optimization-report")
    public MlOptimizationReportResponse optimizationReport(
            @PathVariable Long transactionId,
            @RequestParam(required = false) Integer monthlyVolume,
            @RequestParam(required = false) Integer yearlyVolume
    ) {
        System.out.println("HIT optimization-report endpoint, transactionId=" + transactionId);

        return mlOptimizationService.optimizationReport(
                transactionId,
                monthlyVolume,
                yearlyVolume
        );
    }
}