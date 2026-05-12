package com.example.api.ml.service;

import com.example.api.entity.Transaction;
import com.example.api.entity.MccCode;
import com.example.api.ml.client.MlCoreClient;
import com.example.api.ml.dto.*;
import com.example.api.ml.mapper.MlRuleEngineResultMapper;
import com.example.api.ml.mapper.MlSimulationTransactionMapper;
import com.example.api.ml.mapper.MlTransactionMapper;
import com.example.api.repository.TransactionRepository;
import com.example.api.ruleengine.service.RuleEngineService;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.example.api.ruleengine.model.RuleEngineResult;
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
    private final RuleEngineService ruleEngineService;
    private final MlSimulationTransactionMapper mlSimulationTransactionMapper;

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

            RuleEngineResult currentRuleResult =
                    ruleEngineService.evaluate(currentTransaction);

            MlRuleEngineResult currentMlResult =
                    mlRuleEngineResultMapper.toMlResult(
                            currentTransaction,
                            currentRuleResult
                    );

            Transaction candidateTransaction =
                    buildOptimizationCandidate(currentTransaction);

            RuleEngineResult candidateRuleResult =
                    ruleEngineService.evaluate(candidateTransaction);

            MlRuleEngineResult candidateMlResult =
                    mlRuleEngineResultMapper.toMlResult(
                            candidateTransaction,
                            candidateRuleResult
                    );

            Transaction simulatedTransaction =
                    simulateOptimizedTransaction(
                            currentTransaction,
                            currentMlResult,
                            candidateMlResult
                    );

            RuleEngineResult optimalRuleResult =
                    ruleEngineService.evaluate(simulatedTransaction);

            MlRuleEngineResult optimalMlResult =
                    mlRuleEngineResultMapper.toMlResult(
                            simulatedTransaction,
                            optimalRuleResult
                    );

            MlFeeComparisonRequest request =
                    new MlFeeComparisonRequest(
                            currentMlResult,
                            optimalMlResult,
                            monthlyVolume,
                            yearlyVolume,
                            currentTransaction.getTransactionCurrency()
                    );

            return mlCoreClient.compareFees(request);

        } catch (Exception e) {
            throw new RuntimeException(
                    "ML fee comparison failed for transactionId=" + transactionId,
                    e
            );
        }
    }

    /**
     * Creates an optimized transaction candidate.
     *
     * Important:
     * This does not save anything to the database.
     * It only creates an in-memory transaction object used for ML/rule-engine simulation.
     */
    private Transaction buildOptimizationCandidate(Transaction currentTransaction) {
        Transaction candidate = new Transaction();

        candidate.setTransactionId(currentTransaction.getTransactionId());
        candidate.setClient(currentTransaction.getClient());
        candidate.setMerchant(currentTransaction.getMerchant());
        candidate.setMccCode(currentTransaction.getMccCode());
        candidate.setCard(currentTransaction.getCard());
        candidate.setAcquiringPartner(currentTransaction.getAcquiringPartner());
        candidate.setIssuerBank(currentTransaction.getIssuerBank());
        candidate.setCardNetwork(currentTransaction.getCardNetwork());
        candidate.setTransactionAmount(currentTransaction.getTransactionAmount());
        candidate.setTransactionCurrency(currentTransaction.getTransactionCurrency());
        candidate.setTransactionChannel(currentTransaction.getTransactionChannel());
        candidate.setAuthorizationDatetime(currentTransaction.getAuthorizationDatetime());
        candidate.setClearingDatetime(currentTransaction.getClearingDatetime());
        candidate.setTransactionStatus(currentTransaction.getTransactionStatus());
        candidate.setRegion(currentTransaction.getRegion());

        candidate.setIs3dsAuthenticated("Y");
        candidate.setEciValue("05");

        if (currentTransaction.getAuthorizationDatetime() != null) {
            candidate.setClearingDatetime(
                    currentTransaction.getAuthorizationDatetime().plusHours(8)
            );
        }

        return candidate;
    }

    private Transaction buildDemoTransaction(Long transactionId) {
        Transaction tx = new Transaction();

        MccCode demoMccCode = new MccCode();
        demoMccCode.setMccCode("5411");
        demoMccCode.setMccDescription("Grocery Stores, Supermarkets");

        tx.setTransactionId(transactionId);
        tx.setMccCode(demoMccCode);
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

        RuleEngineResult currentRuleResult =
                ruleEngineService.evaluate(currentTransaction);

        MlRuleEngineResult currentMlResult =
                mlRuleEngineResultMapper.toMlResult(
                        currentTransaction,
                        currentRuleResult
                );

        Transaction candidateTransaction =
                buildOptimizationCandidate(currentTransaction);

        RuleEngineResult candidateRuleResult =
                ruleEngineService.evaluate(candidateTransaction);

        MlRuleEngineResult candidateMlResult =
                mlRuleEngineResultMapper.toMlResult(
                        candidateTransaction,
                        candidateRuleResult
                );

        MlRecommendationRequest request =
                new MlRecommendationRequest(
                        currentMlResult,
                        candidateMlResult
                );

        return mlCoreClient.prioritizeRecommendations(request);
    }

    public String simulateTransaction(Long transactionId) {

        Transaction currentTransaction = transactionRepository.findById(transactionId)
                .orElseGet(() -> buildDemoTransaction(transactionId));

        RuleEngineResult currentRuleResult =
                ruleEngineService.evaluate(currentTransaction);

        MlRuleEngineResult currentMlResult =
                mlRuleEngineResultMapper.toMlResult(
                        currentTransaction,
                        currentRuleResult
                );

        Transaction candidateTransaction =
                buildOptimizationCandidate(currentTransaction);

        RuleEngineResult candidateRuleResult =
                ruleEngineService.evaluate(candidateTransaction);

        MlRuleEngineResult candidateMlResult =
                mlRuleEngineResultMapper.toMlResult(
                        candidateTransaction,
                        candidateRuleResult
                );

        Transaction simulatedTransaction =
                simulateOptimizedTransaction(
                        currentTransaction,
                        currentMlResult,
                        candidateMlResult
                );

        PythonTransactionInput simulatedPythonTransaction =
                mlTransactionMapper.toMlInput(simulatedTransaction);

        try {
            return objectMapper.writeValueAsString(simulatedPythonTransaction);
        } catch (Exception e) {
            throw new RuntimeException("Failed to serialize simulated transaction", e);
        }
    }

    public String missedConditions(Long transactionId) {

        Transaction currentTransaction = transactionRepository.findById(transactionId)
                .orElseGet(() -> buildDemoTransaction(transactionId));

        RuleEngineResult currentRuleResult =
                ruleEngineService.evaluate(currentTransaction);

        MlRuleEngineResult currentMlResult =
                mlRuleEngineResultMapper.toMlResult(
                        currentTransaction,
                        currentRuleResult
                );

        Transaction candidateTransaction =
                buildOptimizationCandidate(currentTransaction);

        RuleEngineResult candidateRuleResult =
                ruleEngineService.evaluate(candidateTransaction);

        MlRuleEngineResult candidateMlResult =
                mlRuleEngineResultMapper.toMlResult(
                        candidateTransaction,
                        candidateRuleResult
                );

        Transaction simulatedTransaction =
                simulateOptimizedTransaction(
                        currentTransaction,
                        currentMlResult,
                        candidateMlResult
                );

        RuleEngineResult optimalRuleResult =
                ruleEngineService.evaluate(simulatedTransaction);

        MlRuleEngineResult optimalMlResult =
                mlRuleEngineResultMapper.toMlResult(
                        simulatedTransaction,
                        optimalRuleResult
                );

        MlMissedConditionRequest request =
                new MlMissedConditionRequest(
                        currentMlResult,
                        optimalMlResult
                );

        return mlCoreClient.missedConditions(request);
    }

    public String detectPortfolioAnomalies() {

        List<Transaction> transactions = transactionRepository.findAll();

        if (transactions.isEmpty()) {
            transactions = List.of(buildDemoTransaction(1L));
        }

        List<MlRuleEngineResult> results = transactions.stream()
                .map(transaction -> {
                    RuleEngineResult ruleResult =
                            ruleEngineService.evaluate(transaction);

                    return mlRuleEngineResultMapper.toMlResult(
                            transaction,
                            ruleResult
                    );
                })
                .toList();

        return mlCoreClient.detectAnomalies(results);
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

    private Transaction simulateOptimizedTransaction(
            Transaction currentTransaction,
            MlRuleEngineResult currentMlResult,
            MlRuleEngineResult candidateMlResult
    ) {
        try {
            MlRecommendationRequest recommendationRequest =
                    new MlRecommendationRequest(
                            currentMlResult,
                            candidateMlResult
                    );

            String recommendationsJson =
                    mlCoreClient.prioritizeRecommendations(recommendationRequest);

            JsonNode recommendationsRoot =
                    objectMapper.readTree(recommendationsJson);

            JsonNode recommendationsNode =
                    recommendationsRoot.get("recommendations");

            List<MlRecommendationSuggestion> recommendations =
                    objectMapper.convertValue(
                            recommendationsNode,
                            objectMapper.getTypeFactory()
                                    .constructCollectionType(
                                            List.class,
                                            MlRecommendationSuggestion.class
                                    )
                    );

            MlSimulationRequest simulationRequest =
                    new MlSimulationRequest(
                            mlTransactionMapper.toMlInput(currentTransaction),
                            recommendations
                    );

            String simulationJson =
                    mlCoreClient.simulateTransaction(simulationRequest);

            JsonNode simulationRoot =
                    objectMapper.readTree(simulationJson);

            JsonNode simulatedTransactionNode =
                    simulationRoot.get("simulatedTransaction");

            return mlSimulationTransactionMapper.toSimulatedTransaction(
                    currentTransaction,
                    simulatedTransactionNode
            );

        } catch (Exception e) {
            throw new RuntimeException("Failed to simulate optimized transaction", e);
        }
    }
}