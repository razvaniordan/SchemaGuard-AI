package com.example.api.ml.mapper;

import com.example.api.entity.Transaction;
import com.example.api.ml.dto.PythonTransactionInput;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
public class MlTransactionMapper {

    /**
     * Converts the internal Transaction entity into the canonical flattened
     * transaction payload expected by the Python ML Core service.
     *
     * Important:
     * - Do not send nested Java entities to ML.
     * - ML expects country, card, merchant, channel and timing fields flattened.
     * - paymentChannel is not sent from Java; Python derives it from channel.
     */
    public PythonTransactionInput toMlInput(Transaction tx) {
        if (tx == null) {
            return null;
        }

        return new PythonTransactionInput(
                getTransactionId(tx),
                getMerchantId(tx),
                getCardId(tx),
                tx.getTransactionAmount(),
                tx.getTransactionCurrency(),
                getMerchantCountryCode(tx),
                getIssuerCountryCode(tx),
                getRegionCode(tx),
                getCardTypeName(tx),
                getCardBrand(tx),
                mapCardPresence(tx),
                mapChannel(tx.getTransactionChannel()),
                getMccCode(tx),
                mapThreeDs(tx),
                tx.getEciValue(),
                tx.getAuthorizationDatetime() != null
                        ? tx.getAuthorizationDatetime().toString()
                        : null,
                tx.getClearingDatetime() != null
                        ? tx.getClearingDatetime().toString()
                        : null,
                calculateClearingDelayDays(tx)
        );
    }

    private String getTransactionId(Transaction tx) {
        return tx.getTransactionId() != null
                ? tx.getTransactionId().toString()
                : null;
    }

    private String getMerchantId(Transaction tx) {
        return tx.getMerchant() != null && tx.getMerchant().getMerchantId() != null
                ? tx.getMerchant().getMerchantId().toString()
                : null;
    }

    private String getCardId(Transaction tx) {
        return tx.getCard() != null && tx.getCard().getCardId() != null
                ? tx.getCard().getCardId().toString()
                : null;
    }

    private String getMerchantCountryCode(Transaction tx) {
        return tx.getMerchant() != null && tx.getMerchant().getCountry() != null
                ? tx.getMerchant().getCountry().getCountryCode()
                : null;
    }

    private String getIssuerCountryCode(Transaction tx) {
        return tx.getIssuerBank() != null && tx.getIssuerBank().getCountry() != null
                ? tx.getIssuerBank().getCountry().getCountryCode()
                : null;
    }

    private String getRegionCode(Transaction tx) {
        return tx.getRegion() != null
                ? tx.getRegion().getRegionCode()
                : null;
    }

    private String getCardTypeName(Transaction tx) {
        return tx.getCard() != null && tx.getCard().getCardType() != null
                ? tx.getCard().getCardType().getCardTypeName()
                : null;
    }

    private String getCardBrand(Transaction tx) {
        return tx.getCardNetwork() != null
                ? tx.getCardNetwork().getNetworkName()
                : null;
    }

    private String getMccCode(Transaction tx) {
        return tx.getMerchant() != null && tx.getMerchant().getMcc() != null
                ? tx.getMerchant().getMcc().getMccCode()
                : null;
    }

    /**
     * Converts Java transaction channel enum values into the channel values
     * expected by ML Core.
     *
     * CONTACTLESS is treated as POS because ML/rule-engine optimization
     * logic groups card-present contactless transactions under POS behavior.
     */
    private String mapChannel(Transaction.TransactionChannel channel) {
        if (channel == null) {
            return null;
        }

        return switch (channel) {
            case ECOMMERCE -> "eCommerce";
            case POS -> "POS";
            case MOTO -> "MOTO";
            case CONTACTLESS -> "POS";
        };
    }

    /**
     * Derives card presence from the transaction channel.
     *
     * ECOMMERCE and MOTO are card-not-present flows.
     * POS and CONTACTLESS are card-present flows.
     */
    private String mapCardPresence(Transaction tx) {
        if (tx.getTransactionChannel() == null) {
            return null;
        }

        if (tx.getTransactionChannel() == Transaction.TransactionChannel.ECOMMERCE
                || tx.getTransactionChannel() == Transaction.TransactionChannel.MOTO) {
            return "card_not_present";
        }

        return "card_present";
    }

    /**
     * Converts the legacy Y/N 3DS flag into a boolean value for ML Core.
     */
    private Boolean mapThreeDs(Transaction tx) {
        return "Y".equalsIgnoreCase(tx.getIs3dsAuthenticated());
    }

    /**
     * Calculates clearing delay in full days.
     *
     * This is needed by the ML models for impact prediction,
     * anomaly detection and root-cause analysis.
     */
    private Long calculateClearingDelayDays(Transaction tx) {
        if (tx.getAuthorizationDatetime() == null || tx.getClearingDatetime() == null) {
            return null;
        }

        return Math.max(
                Duration.between(
                        tx.getAuthorizationDatetime(),
                        tx.getClearingDatetime()
                ).toDays(),
                0
        );
    }
}