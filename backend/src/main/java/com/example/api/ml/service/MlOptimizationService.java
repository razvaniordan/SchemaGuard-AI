package com.example.api.ml.service;

import com.example.api.entity.Transaction;
import com.example.api.ml.client.MlCoreClient;
import com.example.api.ml.dto.*;
import com.example.api.ml.mapper.MlRuleEngineResultMapper;
import com.example.api.ml.mapper.MlTransactionMapper;
import com.example.api.repository.TransactionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class MlOptimizationService {

    private final TransactionRepository transactionRepository;
    private final MlRuleEngineResultMapper mlRuleEngineResultMapper;
    private final MlTransactionMapper mlTransactionMapper;
    private final MlCoreClient mlCoreClient;
    private final ObjectMapper objectMapper;

    // TODO: Replace with your real rule engine service.
    // private final RuleEngineService ruleEngineService;

    /**
     * Runs the full fee comparison flow:
     *
     * Transaction
     * -> current rule-engine result
     * -> optimized/simulated transaction
     * -> optimal rule-engine result
     * -> Python ML Core compare-fees endpoint
     */
    public String compareFees(
            Long transactionId,
            Integer monthlyVolume,
            Integer yearlyVolume
    ) {
        try {
            System.out.println("ML fee comparison started for transactionId=" + transactionId);

            Transaction currentTransaction = transactionRepository.findById(transactionId)
                    .orElseGet(() -> {
                        System.out.println("Transaction not found. Using demo transaction for ML test.");
                        return buildDemoTransaction(transactionId);
                    });

            System.out.println("Transaction found: " + currentTransaction.getTransactionId());

            String currentCategory = "Ecom Non-Secure Credit";
            Double currentFeeRate = 0.0185;
            Double currentFeeAmount = currentTransaction.getTransactionAmount()
                    .multiply(java.math.BigDecimal.valueOf(currentFeeRate))
                    .doubleValue();

            Transaction optimizedTransaction = buildOptimizedTransaction(currentTransaction);

            String optimalCategory = "Ecom Secure Preferred Credit";
            Double optimalFeeRate = 0.0125;
            Double optimalFeeAmount = optimizedTransaction.getTransactionAmount()
                    .multiply(java.math.BigDecimal.valueOf(optimalFeeRate))
                    .doubleValue();

            MlRuleEngineResult currentMlResult =
                    mlRuleEngineResultMapper.toMlResult(
                            currentTransaction,
                            currentCategory,
                            currentFeeRate,
                            currentFeeAmount
                    );

            MlRuleEngineResult optimalMlResult =
                    mlRuleEngineResultMapper.toMlResult(
                            optimizedTransaction,
                            optimalCategory,
                            optimalFeeRate,
                            optimalFeeAmount
                    );

            MlFeeComparisonRequest request =
                    new MlFeeComparisonRequest(
                            currentMlResult,
                            optimalMlResult,
                            monthlyVolume,
                            yearlyVolume,
                            currentTransaction.getTransactionCurrency()
                    );

            System.out.println("Calling Python ML compare-fees...");
            System.out.println("ML request object:");
            System.out.println(request);
            return mlCoreClient.compareFees(request);

        } catch (Exception e) {
            System.out.println("ML fee comparison failed for transactionId=" + transactionId);
            e.printStackTrace();
            throw e;
        }
    }

    /**
     * Creates an optimized transaction candidate.
     *
     * Important:
     * This does not save anything to the database.
     * It only creates an in-memory transaction object used for ML/rule-engine simulation.
     */
    private Transaction buildOptimizedTransaction(Transaction currentTransaction) {
        Transaction optimized = new Transaction();

        optimized.setTransactionId(currentTransaction.getTransactionId());
        optimized.setClient(currentTransaction.getClient());
        optimized.setMerchant(currentTransaction.getMerchant());
        optimized.setCard(currentTransaction.getCard());
        optimized.setAcquiringPartner(currentTransaction.getAcquiringPartner());
        optimized.setIssuerBank(currentTransaction.getIssuerBank());
        optimized.setCardNetwork(currentTransaction.getCardNetwork());
        optimized.setTransactionAmount(currentTransaction.getTransactionAmount());
        optimized.setTransactionCurrency(currentTransaction.getTransactionCurrency());
        optimized.setTransactionChannel(currentTransaction.getTransactionChannel());
        optimized.setAuthorizationDatetime(currentTransaction.getAuthorizationDatetime());
        optimized.setTransactionStatus(currentTransaction.getTransactionStatus());
        optimized.setRegion(currentTransaction.getRegion());

        // MVP optimization: enable 3DS.
        optimized.setIs3dsAuthenticated("Y");
        optimized.setEciValue("05");

        // MVP optimization: faster clearing.
        if (currentTransaction.getAuthorizationDatetime() != null) {
            optimized.setClearingDatetime(
                    currentTransaction.getAuthorizationDatetime().plusHours(8)
            );
        } else {
            optimized.setClearingDatetime(currentTransaction.getClearingDatetime());
        }

        return optimized;
    }

    private Transaction buildDemoTransaction(Long transactionId) {
        Transaction tx = new Transaction();

        tx.setTransactionId(transactionId);
        tx.setTransactionAmount(java.math.BigDecimal.valueOf(100));
        tx.setTransactionCurrency("RON");
        tx.setTransactionChannel(Transaction.TransactionChannel.ECOMMERCE);
        tx.setAuthorizationDatetime(java.time.LocalDateTime.of(2026, 5, 8, 10, 0));
        tx.setClearingDatetime(java.time.LocalDateTime.of(2026, 5, 10, 10, 0));
        tx.setTransactionStatus(Transaction.TransactionStatus.APPROVED);
        tx.setIs3dsAuthenticated("N");
        tx.setEciValue("07");

        return tx;
    }

    public String prioritizeRecommendations(Long transactionId) {

        Transaction currentTransaction = transactionRepository.findById(transactionId)
                .orElseGet(() -> buildDemoTransaction(transactionId));

        String currentCategory = "Ecom Non-Secure Credit";
        Double currentFeeRate = 0.0185;
        Double currentFeeAmount = currentTransaction.getTransactionAmount()
                .multiply(java.math.BigDecimal.valueOf(currentFeeRate))
                .doubleValue();

        Transaction optimizedTransaction = buildOptimizedTransaction(currentTransaction);

        String optimalCategory = "Ecom Secure Preferred Credit";
        Double optimalFeeRate = 0.0125;
        Double optimalFeeAmount = optimizedTransaction.getTransactionAmount()
                .multiply(java.math.BigDecimal.valueOf(optimalFeeRate))
                .doubleValue();

        MlRuleEngineResult currentMlResult =
                mlRuleEngineResultMapper.toMlResult(
                        currentTransaction,
                        currentCategory,
                        currentFeeRate,
                        currentFeeAmount
                );

        MlRuleEngineResult optimalMlResult =
                mlRuleEngineResultMapper.toMlResult(
                        optimizedTransaction,
                        optimalCategory,
                        optimalFeeRate,
                        optimalFeeAmount
                );

        MlRecommendationRequest request =
                new MlRecommendationRequest(currentMlResult, optimalMlResult);

        return mlCoreClient.prioritizeRecommendations(request);
    }

    public String simulateTransaction(Long transactionId) {

        Transaction transaction = transactionRepository.findById(transactionId)
                .orElseGet(() -> buildDemoTransaction(transactionId));

        PythonTransactionInput pythonTransaction =
                mlTransactionMapper.toMlInput(transaction);

        MlRuleEngineResult currentResult =
                mlRuleEngineResultMapper.toMlResult(
                        transaction,
                        "Ecom Non-Secure Credit",
                        0.0185,
                        transaction.getTransactionAmount()
                                .multiply(java.math.BigDecimal.valueOf(0.0185))
                                .doubleValue()
                );

        Transaction optimizedTransaction = buildOptimizedTransaction(transaction);

        MlRuleEngineResult optimalResult =
                mlRuleEngineResultMapper.toMlResult(
                        optimizedTransaction,
                        "Ecom Secure Preferred Credit",
                        0.0125,
                        optimizedTransaction.getTransactionAmount()
                                .multiply(java.math.BigDecimal.valueOf(0.0125))
                                .doubleValue()
                );

        MlRecommendationRequest recommendationRequest =
                new MlRecommendationRequest(currentResult, optimalResult);

        String recommendationsJson =
                mlCoreClient.prioritizeRecommendations(recommendationRequest);

        try {
            JsonNode root = objectMapper.readTree(recommendationsJson);
            JsonNode recommendationsNode = root.get("recommendations");

            List<MlRecommendationSuggestion> recommendations =
                    objectMapper.readerForListOf(MlRecommendationSuggestion.class)
                            .readValue(recommendationsNode);

            MlSimulationRequest simulationRequest =
                    new MlSimulationRequest(pythonTransaction, recommendations);

            return mlCoreClient.simulateTransaction(simulationRequest);

        } catch (Exception e) {
            throw new RuntimeException("Failed to simulate transaction", e);
        }
    }

    public String missedConditions(Long transactionId) {

        Transaction transaction = transactionRepository.findById(transactionId)
                .orElseGet(() -> buildDemoTransaction(transactionId));

        MlRuleEngineResult currentResult =
                mlRuleEngineResultMapper.toMlResult(
                        transaction,
                        "Ecom Non-Secure Credit",
                        0.0185,
                        transaction.getTransactionAmount()
                                .multiply(java.math.BigDecimal.valueOf(0.0185))
                                .doubleValue()
                );

        Transaction optimizedTransaction = buildOptimizedTransaction(transaction);

        MlRuleEngineResult optimalResult =
                mlRuleEngineResultMapper.toMlResult(
                        optimizedTransaction,
                        "Ecom Secure Preferred Credit",
                        0.0125,
                        optimizedTransaction.getTransactionAmount()
                                .multiply(java.math.BigDecimal.valueOf(0.0125))
                                .doubleValue()
                );

        MlMissedConditionRequest request =
                new MlMissedConditionRequest(currentResult, optimalResult);

        return mlCoreClient.missedConditions(request);
    }

    public String detectPortfolioAnomalies() {

        List<Transaction> transactions = transactionRepository.findAll();

        List<MlRuleEngineResult> results = transactions.stream()
                .map(transaction -> {
                    double feeRate = resolveDemoFeeRate(transaction);
                    double feeAmount = transaction.getTransactionAmount()
                            .multiply(java.math.BigDecimal.valueOf(feeRate))
                            .doubleValue();

                    String category = resolveDemoCategory(transaction);

                    return mlRuleEngineResultMapper.toMlResult(
                            transaction,
                            category,
                            feeRate,
                            feeAmount
                    );
                })
                .toList();

        return mlCoreClient.detectAnomalies(results);
    }

    private double resolveDemoFeeRate(Transaction transaction) {
        if ("Y".equalsIgnoreCase(transaction.getIs3dsAuthenticated())) {
            return 0.0125;
        }

        return 0.0185;
    }

    private String resolveDemoCategory(Transaction transaction) {
        if ("Y".equalsIgnoreCase(transaction.getIs3dsAuthenticated())) {
            return "Ecom Secure Preferred Credit";
        }

        return "Ecom Non-Secure Credit";
    }

    public MlOptimizationReportResponse optimizationReport(
            Long transactionId,
            Integer monthlyVolume,
            Integer yearlyVolume
    ) {
        try {
            String feeComparisonJson = compareFees(
                    transactionId,
                    monthlyVolume,
                    yearlyVolume
            );

            String missedConditionsJson = missedConditions(transactionId);

            String recommendationsJson = prioritizeRecommendations(transactionId);

            String anomaliesJson = detectPortfolioAnomalies();

            JsonNode feeComparison = objectMapper.readTree(feeComparisonJson);
            JsonNode missedConditions = objectMapper.readTree(missedConditionsJson);
            JsonNode rankedRecommendations = objectMapper.readTree(recommendationsJson);
            JsonNode anomalyInsights = objectMapper.readTree(anomaliesJson);

            JsonNode savingsProjections = objectMapper.createObjectNode()
                    .put("monthlyProjectedSavings", feeComparison.path("monthlyProjectedSavings").asDouble())
                    .put("yearlyProjectedSavings", feeComparison.path("yearlyProjectedSavings").asDouble())
                    .put("currency", feeComparison.path("currency").asText())
                    .put("mlPredictedSavings", feeComparison.path("mlPredictedSavings").asDouble())
                    .put("mlConfidence", feeComparison.path("mlConfidence").asDouble());

            String summary = buildOptimizationSummary(
                    feeComparison,
                    missedConditions,
                    rankedRecommendations,
                    anomalyInsights
            );

            return new MlOptimizationReportResponse(
                    transactionId,
                    summary,
                    feeComparison,
                    savingsProjections,
                    missedConditions,
                    rankedRecommendations,
                    anomalyInsights
            );

        } catch (Exception e) {
            throw new RuntimeException("Failed to build optimization report", e);
        }
    }

    private String buildOptimizationSummary(
            JsonNode feeComparison,
            JsonNode missedConditions,
            JsonNode rankedRecommendations,
            JsonNode anomalyInsights
    ) {
        double absoluteSavings = feeComparison.path("absoluteSavings").asDouble();
        double percentageSavings = feeComparison.path("percentageSavings").asDouble();
        double monthlySavings = feeComparison.path("monthlyProjectedSavings").asDouble();
        double yearlySavings = feeComparison.path("yearlyProjectedSavings").asDouble();
        String currency = feeComparison.path("currency").asText("RON");

        int missedCount = missedConditions.path("missedConditions").size();
        int recommendationCount = rankedRecommendations.path("recommendations").size();
        int anomalyCount = anomalyInsights.path("anomalies").size();

        return "Optimization analysis found potential savings of "
                + absoluteSavings + " " + currency
                + " per transaction (" + percentageSavings + "%). "
                + "Projected savings are "
                + monthlySavings + " " + currency + " monthly and "
                + yearlySavings + " " + currency + " yearly. "
                + "Detected " + missedCount + " missed optimization conditions, "
                + recommendationCount + " ranked recommendations, and "
                + anomalyCount + " anomaly insights.";
    }
}