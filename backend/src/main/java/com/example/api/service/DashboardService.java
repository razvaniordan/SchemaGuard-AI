package com.example.api.service;

import com.example.api.dto.dashboard.CategoryTransitionResponse;
import com.example.api.dto.dashboard.DashboardKpiResponse;
import com.example.api.dto.dashboard.DashboardOverviewResponse;
import com.example.api.dto.dashboard.MerchantOptimizationResponse;
import com.example.api.dto.dashboard.MonthlySavingsResponse;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
public class DashboardService {

    private final JdbcTemplate jdbcTemplate;

    public DashboardService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional(readOnly = true)
    public DashboardOverviewResponse getOverview() {
        return new DashboardOverviewResponse(
                getKpis(),
                getMonthlySavings(),
                getTopMerchants(),
                getCategoryTransitions()
        );
    }

    private DashboardKpiResponse getKpis() {
        String sql = """
                SELECT
                    COUNT(*) AS transaction_count,
                    COALESCE(SUM(transaction_amount), 0) AS total_transaction_amount,
                    COALESCE(SUM(current_interchange_fee_amount), 0) AS total_current_fee_amount,
                    COALESCE(SUM(optimal_interchange_fee_amount), 0) AS total_optimal_fee_amount,
                    COALESCE(SUM(saving_amount), 0) AS total_saving_amount,
                    COALESCE(CAST(AVG(saving_percentage) AS NUMERIC(7, 4)), 0) AS avg_saving_percentage
                FROM analytics.fact_transaction_analysis
                """;

        return jdbcTemplate.queryForObject(sql, (rs, rowNum) -> new DashboardKpiResponse(
                rs.getLong("transaction_count"),
                rs.getBigDecimal("total_transaction_amount"),
                rs.getBigDecimal("total_current_fee_amount"),
                rs.getBigDecimal("total_optimal_fee_amount"),
                rs.getBigDecimal("total_saving_amount"),
                rs.getBigDecimal("avg_saving_percentage")
        ));
    }

    private List<MonthlySavingsResponse> getMonthlySavings() {
        String sql = """
                SELECT
                    d.year_number,
                    d.month_number,
                    d.month_name,
                    COUNT(*) AS transaction_count,
                    COALESCE(SUM(f.transaction_amount), 0) AS total_transaction_amount,
                    COALESCE(SUM(f.current_interchange_fee_amount), 0) AS total_current_fee_amount,
                    COALESCE(SUM(f.optimal_interchange_fee_amount), 0) AS total_optimal_fee_amount,
                    COALESCE(SUM(f.saving_amount), 0) AS total_saving_amount,
                    COALESCE(CAST(AVG(f.saving_percentage) AS NUMERIC(7, 4)), 0) AS avg_saving_percentage
                FROM analytics.fact_transaction_analysis f
                JOIN analytics.dim_date d ON d.date_key = f.authorization_date_key
                GROUP BY d.year_number, d.month_number, d.month_name
                ORDER BY d.year_number, d.month_number
                """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> new MonthlySavingsResponse(
                rs.getInt("year_number"),
                rs.getInt("month_number"),
                rs.getString("month_name"),
                rs.getLong("transaction_count"),
                rs.getBigDecimal("total_transaction_amount"),
                rs.getBigDecimal("total_current_fee_amount"),
                rs.getBigDecimal("total_optimal_fee_amount"),
                rs.getBigDecimal("total_saving_amount"),
                rs.getBigDecimal("avg_saving_percentage")
        ));
    }

    private List<MerchantOptimizationResponse> getTopMerchants() {
        String sql = """
                SELECT
                    m.merchant_key,
                    m.source_merchant_id,
                    m.merchant_name,
                    m.mcc_code,
                    m.mcc_description,
                    COUNT(*) AS transaction_count,
                    COALESCE(SUM(f.transaction_amount), 0) AS total_transaction_amount,
                    COALESCE(SUM(f.current_interchange_fee_amount), 0) AS total_current_fee_amount,
                    COALESCE(SUM(f.optimal_interchange_fee_amount), 0) AS total_optimal_fee_amount,
                    COALESCE(SUM(f.saving_amount), 0) AS total_saving_amount,
                    COALESCE(CAST(AVG(f.saving_percentage) AS NUMERIC(7, 4)), 0) AS avg_saving_percentage
                FROM analytics.fact_transaction_analysis f
                JOIN analytics.dim_merchant m ON m.merchant_key = f.merchant_key
                GROUP BY m.merchant_key, m.source_merchant_id, m.merchant_name, m.mcc_code, m.mcc_description
                ORDER BY total_saving_amount DESC, transaction_count DESC
                LIMIT 10
                """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> new MerchantOptimizationResponse(
                rs.getLong("merchant_key"),
                rs.getLong("source_merchant_id"),
                rs.getString("merchant_name"),
                rs.getString("mcc_code"),
                rs.getString("mcc_description"),
                rs.getLong("transaction_count"),
                rs.getBigDecimal("total_transaction_amount"),
                rs.getBigDecimal("total_current_fee_amount"),
                rs.getBigDecimal("total_optimal_fee_amount"),
                rs.getBigDecimal("total_saving_amount"),
                rs.getBigDecimal("avg_saving_percentage")
        ));
    }

    private List<CategoryTransitionResponse> getCategoryTransitions() {
        String sql = """
                SELECT
                    current_cat.category_key AS current_category_key,
                    current_cat.category_name AS current_category_name,
                    optimal_cat.category_key AS optimal_category_key,
                    optimal_cat.category_name AS optimal_category_name,
                    COUNT(*) AS transaction_count,
                    COALESCE(SUM(f.current_interchange_fee_amount), 0) AS total_current_fee_amount,
                    COALESCE(SUM(f.optimal_interchange_fee_amount), 0) AS total_optimal_fee_amount,
                    COALESCE(SUM(f.saving_amount), 0) AS total_saving_amount,
                    COALESCE(CAST(AVG(f.saving_percentage) AS NUMERIC(7, 4)), 0) AS avg_saving_percentage
                FROM analytics.fact_transaction_analysis f
                JOIN analytics.dim_interchange_category current_cat ON current_cat.category_key = f.current_category_key
                JOIN analytics.dim_interchange_category optimal_cat ON optimal_cat.category_key = f.optimal_category_key
                GROUP BY current_cat.category_key, current_cat.category_name, optimal_cat.category_key, optimal_cat.category_name
                ORDER BY total_saving_amount DESC, transaction_count DESC
                LIMIT 10
                """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> new CategoryTransitionResponse(
                rs.getLong("current_category_key"),
                rs.getString("current_category_name"),
                rs.getLong("optimal_category_key"),
                rs.getString("optimal_category_name"),
                rs.getLong("transaction_count"),
                rs.getBigDecimal("total_current_fee_amount"),
                rs.getBigDecimal("total_optimal_fee_amount"),
                rs.getBigDecimal("total_saving_amount"),
                rs.getBigDecimal("avg_saving_percentage")
        ));
    }
}
