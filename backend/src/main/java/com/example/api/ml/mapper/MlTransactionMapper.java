package com.example.api.ml.mapper;

import com.example.api.entity.Transaction;
import com.example.api.ml.dto.PythonTransactionInput;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
public class MlTransactionMapper {

    public PythonTransactionInput toMlInput(Transaction tx) {
        if (tx == null) {
            return null;
        }

        return new PythonTransactionInput(
                tx.getTransactionId() != null ? tx.getTransactionId().toString() : null,

                tx.getMerchant() != null && tx.getMerchant().getMerchantId() != null
                        ? tx.getMerchant().getMerchantId().toString()
                        : null,

                tx.getCard() != null && tx.getCard().getCardId() != null
                        ? tx.getCard().getCardId().toString()
                        : null,

                tx.getTransactionAmount(),
                tx.getTransactionCurrency(),

                tx.getMerchant() != null && tx.getMerchant().getCountry() != null
                        ? tx.getMerchant().getCountry().getCountryCode()
                        : null,

                tx.getIssuerBank() != null && tx.getIssuerBank().getCountry() != null
                        ? tx.getIssuerBank().getCountry().getCountryCode()
                        : null,

                tx.getRegion() != null
                        ? tx.getRegion().getRegionCode()
                        : null,

                tx.getCard() != null && tx.getCard().getCardType() != null
                        ? tx.getCard().getCardType().getCardTypeName()
                        : null,

                tx.getCardNetwork() != null
                        ? tx.getCardNetwork().getNetworkName()
                        : null,

                mapCardPresence(tx),
                mapChannel(tx.getTransactionChannel()),

                tx.getMerchant() != null && tx.getMerchant().getMcc() != null
                        ? tx.getMerchant().getMcc().getMccCode()
                        : null,

                "Y".equalsIgnoreCase(tx.getIs3dsAuthenticated()),
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

    private String mapCardPresence(Transaction tx) {
        if (tx.getTransactionChannel() == Transaction.TransactionChannel.ECOMMERCE
                || tx.getTransactionChannel() == Transaction.TransactionChannel.MOTO) {
            return "card_not_present";
        }

        return "card_present";
    }

    private Long calculateClearingDelayDays(Transaction tx) {
        if (tx.getAuthorizationDatetime() == null || tx.getClearingDatetime() == null) {
            return null;
        }

        return Duration.between(
                tx.getAuthorizationDatetime(),
                tx.getClearingDatetime()
        ).toDays();
    }
}