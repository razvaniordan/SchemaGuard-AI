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
        Transaction currentTransaction = transactionRepository.findById(transactionId)
                .orElseThrow(() -> new IllegalArgumentException(
                        "Transaction not found with id: " + transactionId
                ));

        /*
         * STEP 1:
         * Run rule engine for the current/original transaction.
         *
         * Replace these demo values with the real rule-engine response.
         */
        String currentCategory = "Ecom Non-Secure Credit";
        Double currentFeeRate = 0.0185;
        Double currentFeeAmount = currentTransaction.getTransactionAmount()
                .multiply(java.math.BigDecimal.valueOf(currentFeeRate))
                .doubleValue();

        /*
         * STEP 2:
         * Build an optimized transaction candidate.
         *
         * For now this is a simple MVP optimization:
         * - enable 3DS
         * - reduce clearing date to same day if possible
         *
         * Later this should come from simulation/recommendation logic.
         */
        Transaction optimizedTransaction = buildOptimizedTransaction(currentTransaction);

        /*
         * STEP 3:
         * Run rule engine for the optimized transaction.
         *
         * Replace these demo values with the real rule-engine response.
         */
        String optimalCategory = "Ecom Secure Preferred Credit";
        Double optimalFeeRate = 0.0125;
        Double optimalFeeAmount = optimizedTransaction.getTransactionAmount()
                .multiply(java.math.BigDecimal.valueOf(optimalFeeRate))
                .doubleValue();

        /*
         * STEP 4:
         * Convert current and optimized rule-engine outputs into ML Core DTOs.
         */
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

        /*
         * STEP 5:
         * Build request for Python ML Core.
         */
        MlFeeComparisonRequest request =
                new MlFeeComparisonRequest(
                        currentMlResult,
                        optimalMlResult,
                        monthlyVolume,
                        yearlyVolume,
                        currentTransaction.getTransactionCurrency()
                );

        /*
         * STEP 6:
         * Call Python ML Core /ml-core/compare-fees.
         */
        return mlCoreClient.compareFees(request);
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
}