package com.example.api.ml.service;

import com.example.api.entity.Transaction;
import com.example.api.ml.client.MlCoreClient;
import com.example.api.ml.dto.MlFeeComparisonRequest;
import com.example.api.ml.dto.MlRuleEngineResult;
import com.example.api.ml.mapper.MlRuleEngineResultMapper;
import com.example.api.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class MlOptimizationService {

    private final TransactionRepository transactionRepository;
    private final MlRuleEngineResultMapper mlRuleEngineResultMapper;
    private final MlCoreClient mlCoreClient;

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
}