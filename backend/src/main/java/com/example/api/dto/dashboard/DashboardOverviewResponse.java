package com.example.api.dto.dashboard;

import java.util.List;

public record DashboardOverviewResponse(
        DashboardKpiResponse kpis,
        List<MonthlySavingsResponse> monthlySavings,
        List<MerchantOptimizationResponse> topMerchants,
        List<CategoryTransitionResponse> categoryTransitions
) {
}
