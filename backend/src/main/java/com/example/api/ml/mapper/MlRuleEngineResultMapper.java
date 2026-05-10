package com.example.api.ml.mapper;

import com.example.api.entity.Transaction;
import com.example.api.ml.dto.MlRuleEngineResult;
import com.example.api.ml.dto.PythonTransactionInput;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class MlRuleEngineResultMapper {

    private final MlTransactionMapper mlTransactionMapper;

    /**
     * Converts rule-engine output + Transaction entity into the ML Core format.
     *
     * ML Core must receive:
     * - category from the rule engine
     * - feeRate from the rule engine
     * - feeAmount from the rule engine fee calculation
     * - flattened transaction payload
     *
     * Important:
     * ML should not calculate the fee by itself.
     * The rule engine remains the source of truth for category, feeRate and feeAmount.
     */
    public MlRuleEngineResult toMlResult(
            Transaction transaction,
            String category,
            Double feeRate,
            Double feeAmount
    ) {
        PythonTransactionInput mlTransaction =
                mlTransactionMapper.toMlInput(transaction);

        return new MlRuleEngineResult(
                category,
                normalizeFeeRate(feeRate),
                feeAmount,
                mlTransaction
        );
    }

    /**
     * Ensures feeRate is stored as a decimal fraction.
     *
     * Correct:
     * 0.0185 = 1.85%
     *
     * Incorrect:
     * 1.85 = 1.85%
     */
    private Double normalizeFeeRate(Double feeRate) {
        if (feeRate == null) {
            return null;
        }

        if (feeRate > 1) {
            return feeRate / 100;
        }

        return feeRate;
    }
}