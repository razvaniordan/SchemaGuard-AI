package com.example.api.ruleengine.service;

import com.example.api.entity.Transaction;
import com.example.api.ruleengine.model.RuleEngineResult;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;

@Service
public class RuleEngineService {

    public RuleEngineResult evaluate(Transaction transaction) {

        if (transaction == null) {
            throw new IllegalArgumentException("Transaction must not be null");
        }

        if (transaction.getTransactionAmount() == null) {
            throw new IllegalArgumentException("Transaction amount must not be null");
        }

        String channel = normalizeChannel(transaction);
        String cardPresence = resolveCardPresence(transaction);
        boolean is3ds = isThreeDsAuthenticated(transaction);
        long clearingDelayDays = calculateClearingDelayDays(transaction);

        String cardNetwork = getCardNetwork(transaction);
        String cardType = getCardType(transaction);
        String mcc = getMcc(transaction);
        String region = getRegion(transaction);

        if (isEcommerce(channel) && is3ds && clearingDelayDays <= 1) {
            return buildResult(
                    transaction,
                    "Ecom Secure Preferred Credit",
                    0.0125,
                    "ECOM_SECURE_FAST_CLEARING",
                    "E-commerce Secure Fast Clearing",
                    "Transaction qualified for preferred eCommerce pricing because it is 3DS authenticated and cleared within 1 day."
            );
        }

        if (isEcommerce(channel) && is3ds) {
            return buildResult(
                    transaction,
                    "Ecom Secure Credit",
                    0.0145,
                    "ECOM_SECURE",
                    "E-commerce Secure",
                    "Transaction qualified for secure eCommerce pricing because 3DS authentication was present."
            );
        }

        if (isEcommerce(channel) && !is3ds) {

            return buildResult(
                    transaction,
                    "Ecom Non-Secure Credit",
                    0.0185,
                    "ECOM_NON_SECURE",
                    "E-commerce Non-Secure",
                    "Transaction received a higher fee because 3DS authentication was not present."
            );
        }
        
        if (isPos(channel) && "card_present".equals(cardPresence) && clearingDelayDays <= 1) {
            return buildResult(
                    transaction,
                    "POS Preferred Credit",
                    0.0110,
                    "POS_CARD_PRESENT_FAST_CLEARING",
                    "POS Card-Present Fast Clearing",
                    "Card-present POS transaction qualified for preferred pricing because it cleared within 1 day."
            );
        }

        if (isPos(channel) && "card_present".equals(cardPresence)) {
            return buildResult(
                    transaction,
                    "POS Standard Credit",
                    0.0130,
                    "POS_CARD_PRESENT",
                    "POS Card-Present Standard",
                    "Card-present POS transaction qualified for standard POS pricing."
            );
        }

        if (isHighRiskMcc(mcc)) {
            return buildResult(
                    transaction,
                    "High Risk MCC Standard",
                    0.0220,
                    "HIGH_RISK_MCC",
                    "High Risk MCC",
                    "Transaction matched a higher-risk MCC category."
            );
        }

        if (isCrossRegion(region)) {
            return buildResult(
                    transaction,
                    "Cross Region Standard",
                    0.0200,
                    "CROSS_REGION",
                    "Cross Region Standard",
                    "Transaction matched cross-region pricing."
            );
        }

        return buildResult(
                transaction,
                "Standard Card Transaction",
                0.0150,
                "STANDARD_CARD",
                "Standard Card Rate",
                "Transaction matched the standard fallback rule."
        );
    }

    private RuleEngineResult buildResult(
            Transaction transaction,
            String category,
            Double feeRate,
            String appliedRuleCode,
            String appliedRuleName,
            String explanation
    ) {
        BigDecimal feeAmount = transaction.getTransactionAmount()
                .multiply(BigDecimal.valueOf(feeRate))
                .setScale(2, RoundingMode.HALF_UP);

        return new RuleEngineResult(
                category,
                feeRate,
                feeAmount,
                appliedRuleCode,
                appliedRuleName,
                explanation
        );
    }

    private String normalizeChannel(Transaction transaction) {
        if (transaction.getTransactionChannel() == null) {
            return null;
        }

        return switch (transaction.getTransactionChannel()) {
            case ECOMMERCE -> "ECOMMERCE";
            case MOTO -> "MOTO";
            case POS, CONTACTLESS -> "POS";
        };
    }

    private String resolveCardPresence(Transaction transaction) {
        if (transaction.getTransactionChannel() == null) {
            return null;
        }

        return switch (transaction.getTransactionChannel()) {
            case ECOMMERCE, MOTO -> "card_not_present";
            case POS, CONTACTLESS -> "card_present";
        };
    }

    private boolean isThreeDsAuthenticated(Transaction transaction) {
        return "Y".equalsIgnoreCase(transaction.getIs3dsAuthenticated());
    }

    private long calculateClearingDelayDays(Transaction transaction) {
        if (transaction.getAuthorizationDatetime() == null
                || transaction.getClearingDatetime() == null) {
            return Long.MAX_VALUE;
        }

        return Math.max(
                Duration.between(
                        transaction.getAuthorizationDatetime(),
                        transaction.getClearingDatetime()
                ).toDays(),
                0
        );
    }

    private boolean isEcommerce(String channel) {
        return "ECOMMERCE".equals(channel);
    }

    private boolean isPos(String channel) {
        return "POS".equals(channel);
    }

    private String getCardNetwork(Transaction transaction) {
        return transaction.getCardNetwork() != null
                ? transaction.getCardNetwork().getNetworkName()
                : null;
    }

    private String getCardType(Transaction transaction) {
        return transaction.getCard() != null
                && transaction.getCard().getCardType() != null
                ? transaction.getCard().getCardType().getCardTypeName()
                : null;
    }

    private String getMcc(Transaction transaction) {
        return transaction.getMerchant() != null
                && transaction.getMerchant().getMcc() != null
                ? transaction.getMerchant().getMcc().getMccCode()
                : null;
    }

    private String getRegion(Transaction transaction) {
        return transaction.getRegion() != null
                ? transaction.getRegion().getRegionCode()
                : null;
    }

    private boolean isHighRiskMcc(String mcc) {
        if (mcc == null) {
            return false;
        }

        return mcc.equals("7995")
                || mcc.equals("5967")
                || mcc.equals("6012")
                || mcc.equals("6051");
    }

    private boolean isCrossRegion(String region) {
        if (region == null) {
            return false;
        }

        return region.equalsIgnoreCase("INTERREGIONAL")
                || region.equalsIgnoreCase("CROSS_BORDER")
                || region.equalsIgnoreCase("NON_EEA");
    }
}