package com.example.api.ruleengine.service;

import com.example.api.entity.InterchangeRule;
import com.example.api.entity.Transaction;
import com.example.api.repository.InterchangeRuleRepository;
import com.example.api.ruleengine.model.RuleEngineResult;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;

@Service
@RequiredArgsConstructor
public class RuleEngineService {

    private final InterchangeRuleRepository interchangeRuleRepository;

    public RuleEngineResult evaluate(Transaction transaction) {
        validateTransaction(transaction);

        InterchangeRule.ClearingTimeCondition clearingTimeCondition =
                resolveClearingTimeCondition(transaction);

        InterchangeRule rule = interchangeRuleRepository.findBestMatchingRule(
                getCardNetworkId(transaction),
                getMccCode(transaction),
                getCardTypeId(transaction),
                normalizeChannel(transaction),
                getRegionCode(transaction),
                normalizeYesNo(transaction.getIs3dsAuthenticated()),
                clearingTimeCondition != null ? clearingTimeCondition.name() : null
        ).orElseThrow(() -> new IllegalStateException(
                "No interchange rule matched transaction " + transaction.getTransactionId()
        ));

        return buildResult(transaction, rule, clearingTimeCondition);
    }

    private void validateTransaction(Transaction transaction) {
        if (transaction == null) {
            throw new IllegalArgumentException("Transaction must not be null");
        }
        if (transaction.getTransactionAmount() == null) {
            throw new IllegalArgumentException("Transaction amount must not be null");
        }
    }

    private RuleEngineResult buildResult(
            Transaction transaction,
            InterchangeRule rule,
            InterchangeRule.ClearingTimeCondition clearingTimeCondition
    ) {
        BigDecimal feeRate = rule.getFeePercentage()
                .divide(BigDecimal.valueOf(100), 6, RoundingMode.HALF_UP);

        BigDecimal fixedFee = rule.getFixedFeeAmount() != null
                ? rule.getFixedFeeAmount()
                : BigDecimal.ZERO;

        BigDecimal feeAmount = transaction.getTransactionAmount()
                .multiply(feeRate)
                .add(fixedFee)
                .setScale(2, RoundingMode.HALF_UP);

        String categoryName = rule.getCategory() != null
                ? rule.getCategory().getCategoryName()
                : "Unknown Category";

        return new RuleEngineResult(
                categoryName,
                feeRate.doubleValue(),
                feeAmount,
                "RULE_" + rule.getRuleId(),
                categoryName,
                buildExplanation(rule, clearingTimeCondition)
        );
    }

    private String buildExplanation(
            InterchangeRule rule,
            InterchangeRule.ClearingTimeCondition clearingTimeCondition
    ) {
        String categoryName = rule.getCategory() != null
                ? rule.getCategory().getCategoryName()
                : "Unknown Category";

        return "Matched interchange rule " + rule.getRuleId()
                + " with priority " + rule.getRulePriority()
                + " for category " + categoryName
                + ". Fee percentage " + rule.getFeePercentage()
                + "% plus fixed fee " + rule.getFixedFeeAmount()
                + " " + rule.getCurrencyCode()
                + ". Clearing condition: " + (clearingTimeCondition != null ? clearingTimeCondition : "ANY")
                + ".";
    }

    private String normalizeChannel(Transaction transaction) {
        if (transaction.getTransactionChannel() == null) {
            return null;
        }

        if (transaction.getTransactionChannel() == Transaction.TransactionChannel.CONTACTLESS) {
            return Transaction.TransactionChannel.POS.name();
        }

        return transaction.getTransactionChannel().name();
    }

    private InterchangeRule.ClearingTimeCondition resolveClearingTimeCondition(Transaction transaction) {
        if (transaction.getAuthorizationDatetime() == null || transaction.getClearingDatetime() == null) {
            return null;
        }

        long hours = Duration.between(
                transaction.getAuthorizationDatetime(),
                transaction.getClearingDatetime()
        ).toHours();

        return hours <= 24
                ? InterchangeRule.ClearingTimeCondition.LTE_24H
                : InterchangeRule.ClearingTimeCondition.GT_24H;
    }

    private Long getCardNetworkId(Transaction transaction) {
        return transaction.getCardNetwork() != null
                ? transaction.getCardNetwork().getCardNetworkId()
                : null;
    }

    private String getMccCode(Transaction transaction) {
        return transaction.getMccCode() != null
                ? transaction.getMccCode().getMccCode()
                : null;
    }

    private Long getCardTypeId(Transaction transaction) {
        return transaction.getCard() != null && transaction.getCard().getCardType() != null
                ? transaction.getCard().getCardType().getCardTypeId()
                : null;
    }

    private String getRegionCode(Transaction transaction) {
        return transaction.getRegion() != null
                ? transaction.getRegion().getRegionCode()
                : null;
    }

    private String normalizeYesNo(String value) {
        if (value == null) {
            return null;
        }
        return value.trim().toUpperCase();
    }
}