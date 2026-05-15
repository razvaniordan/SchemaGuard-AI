package com.example.api.ml.service;

import com.example.api.entity.Transaction;
import com.example.api.entity.MccCode;
import com.example.api.entity.Client;
import com.example.api.entity.Merchant;
import com.example.api.entity.Card;
import com.example.api.entity.AcquiringPartner;
import com.example.api.entity.Bank;
import com.example.api.entity.CardNetwork;
import com.example.api.entity.Region;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.example.api.ml.client.MlCoreClient;
import com.example.api.ml.cache.PortfolioAnomalyCacheService;
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
        private final PortfolioAnomalyCacheService portfolioAnomalyCacheService;


    private Transaction getExistingTransaction(Long transactionId) {
        return transactionRepository.findById(transactionId)
                .orElseThrow(() -> new IllegalArgumentException(
                        "Transaction not found: " + transactionId
                ));
    }

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

            Transaction currentTransaction = getExistingTransaction(transactionId);

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

            String responseJson = mlCoreClient.compareFees(request);
            JsonNode response = objectMapper.readTree(responseJson);

            ObjectNode enriched = (ObjectNode) response.deepCopy();

            enriched.put("currentCategory", currentRuleResult.category());
            enriched.put("optimalCategory", optimalRuleResult.category());
            enriched.put("optimizedCategory", optimalRuleResult.category());

            enriched.put("currentFeeRate", currentRuleResult.feeRate());
            enriched.put("optimalFeeRate", optimalRuleResult.feeRate());
            enriched.put("optimizedFeeRate", optimalRuleResult.feeRate());

            enriched.put("currentFeeAmount", currentRuleResult.feeAmount());
            enriched.put("optimizedFeeAmount", optimalRuleResult.feeAmount());
            enriched.put("optimalFeeAmount", optimalRuleResult.feeAmount());

            enriched.put("currentAppliedRule", currentRuleResult.category());
            enriched.put("optimalAppliedRule", optimalRuleResult.category());
            enriched.put("optimizedAppliedRule", optimalRuleResult.category());

            return objectMapper.writeValueAsString(enriched);

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

        Client client = new Client();
        client.setClientId(1L);
        client.setClientName("Demo Client");

        Merchant merchant = new Merchant();
        merchant.setMerchantId(1L);
        merchant.setMerchantName("Demo Merchant");

        MccCode demoMccCode = new MccCode();
        demoMccCode.setMccCode("5411");
        demoMccCode.setMccDescription("Grocery Stores, Supermarkets");

        Card card = new Card();
        card.setCardId(1L);

        AcquiringPartner acquiringPartner = new AcquiringPartner();
        acquiringPartner.setAcquiringPartnerId(1L);

        Bank issuerBank = new Bank();
        issuerBank.setBankId(1L);

        CardNetwork cardNetwork = new CardNetwork();
        cardNetwork.setCardNetworkId(1L);

        Region region = new Region();
        region.setRegionCode("EU");

        tx.setTransactionId(transactionId);

        tx.setClient(client);
        tx.setMerchant(merchant);
        tx.setMccCode(demoMccCode);
        tx.setCard(card);
        tx.setAcquiringPartner(acquiringPartner);
        tx.setIssuerBank(issuerBank);
        tx.setCardNetwork(cardNetwork);
        tx.setRegion(region);

        tx.setTransactionAmount(java.math.BigDecimal.valueOf(100));
        tx.setTransactionCurrency("RON");

        tx.setTransactionChannel(Transaction.TransactionChannel.ECOMMERCE);

        tx.setAuthorizationDatetime(
                java.time.LocalDateTime.of(2026, 5, 8, 10, 0)
        );

        tx.setClearingDatetime(
                java.time.LocalDateTime.of(2026, 5, 10, 10, 0)
        );

        tx.setTransactionStatus(Transaction.TransactionStatus.APPROVED);

        tx.setIs3dsAuthenticated("N");
        tx.setEciValue("07");

        return tx;
    }

    public String prioritizeRecommendations(Long transactionId) {

        Transaction currentTransaction = getExistingTransaction(transactionId);

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

        Transaction currentTransaction = getExistingTransaction(transactionId);

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

        Transaction currentTransaction = getExistingTransaction(transactionId);

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

        try {
            var root = objectMapper.createObjectNode();

            root.put("currentCategory", currentRuleResult.category());
            root.put("optimalCategory", optimalRuleResult.category());
            root.put("currentFeeRate", currentRuleResult.feeRate());
            root.put("optimalFeeRate", optimalRuleResult.feeRate());

            var missedConditions = objectMapper.createArrayNode();

            double feeRateImpact = Math.max(
                    currentRuleResult.feeRate() - optimalRuleResult.feeRate(),
                    0
            );

            boolean categoryChanged =
                    currentRuleResult.category() != null
                            && optimalRuleResult.category() != null
                            && !currentRuleResult.category().equals(optimalRuleResult.category());

            if (categoryChanged) {
                var condition = objectMapper.createObjectNode();

                condition.put("condition", "Interchange category");
                condition.put("currentValue", currentRuleResult.category());
                condition.put("optimalValue", optimalRuleResult.category());
                condition.put("impact", feeRateImpact);
                condition.put("confidence", 0.9);
                condition.put(
                        "explanation",
                        "The optimized transaction qualifies for a better interchange category."
                );

                missedConditions.add(condition);
            }

            boolean isEcommerce =
                    currentTransaction.getTransactionChannel() != null
                            && "ECOMMERCE".equalsIgnoreCase(
                            currentTransaction.getTransactionChannel().toString()
                    );

            boolean currentHas3ds =
                    currentTransaction.getIs3dsAuthenticated() != null
                            && "Y".equalsIgnoreCase(currentTransaction.getIs3dsAuthenticated());

            boolean optimizedHas3ds =
                    simulatedTransaction.getIs3dsAuthenticated() != null
                            && "Y".equalsIgnoreCase(simulatedTransaction.getIs3dsAuthenticated());

            if (isEcommerce && !currentHas3ds && optimizedHas3ds) {
                var condition = objectMapper.createObjectNode();

                condition.put("condition", "3DS Authentication");
                condition.put("currentValue", "Not authenticated");
                condition.put("optimalValue", "3DS authenticated");
                condition.put("impact", Math.max(feeRateImpact * 0.6, 0));
                condition.put("confidence", 0.85);
                condition.put(
                        "explanation",
                        "E-commerce transaction is missing 3DS authentication and may qualify for worse interchange fees."
                );

                missedConditions.add(condition);
            }

            Integer clearingDelayDays = null;

            if (currentTransaction.getAuthorizationDatetime() != null
                    && currentTransaction.getClearingDatetime() != null) {
                clearingDelayDays = (int) java.time.Duration.between(
                        currentTransaction.getAuthorizationDatetime(),
                        currentTransaction.getClearingDatetime()
                ).toDays();
            }

            boolean clearingImproved =
                    currentTransaction.getClearingDatetime() != null
                            && simulatedTransaction.getClearingDatetime() != null
                            && !currentTransaction.getClearingDatetime()
                            .equals(simulatedTransaction.getClearingDatetime());

            if (clearingDelayDays != null
                    && clearingDelayDays >= 2
                    && clearingImproved) {
                var condition = objectMapper.createObjectNode();

                condition.put("condition", "Timely Clearing");
                condition.put("currentValue", clearingDelayDays + " days");
                condition.put("optimalValue", "Same day or next day clearing");
                condition.put("impact", Math.max(feeRateImpact * 0.4, 0));
                condition.put("confidence", 0.8);
                condition.put(
                        "explanation",
                        "Delayed clearing may prevent optimal fee qualification."
                );

                missedConditions.add(condition);
            }

            root.set("missedConditions", missedConditions);

            return objectMapper.writeValueAsString(root);

        } catch (Exception e) {
            throw new RuntimeException("Failed to build missed conditions response", e);
        }
    }

    public String detectPortfolioAnomalies() {
                try {
                        return objectMapper.writeValueAsString(portfolioAnomalyCacheService.getSnapshot());
                } catch (Exception e) {
                        throw new RuntimeException("Failed to serialize cached portfolio anomalies", e);
                }
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

            JsonNode feeComparison = objectMapper.readTree(feeComparisonJson);
            JsonNode missedConditions = objectMapper.readTree(missedConditionsJson);
            JsonNode rankedRecommendations = objectMapper.readTree(recommendationsJson);
            JsonNode anomalyInsights = portfolioAnomalyCacheService.getSnapshot();

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