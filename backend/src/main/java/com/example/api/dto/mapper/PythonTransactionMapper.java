package com.example.api.dto.mapper;

import com.example.api.dto.request.PythonClassificationRequest;
import com.example.api.entity.Transaction;
import org.springframework.stereotype.Component;

@Component
public class PythonTransactionMapper {

    public PythonClassificationRequest toPythonInput(Transaction tx) {
        return new PythonClassificationRequest(
                tx.getTransactionId() == null ? null : tx.getTransactionId().toString(),

                tx.getMerchant() == null ? null : tx.getMerchant().getMerchantId().toString(),

                tx.getCard() == null ? null : tx.getCard().getCardId().toString(),

                tx.getTransactionAmount(),
                tx.getTransactionCurrency(),

                tx.getMerchant() == null || tx.getMerchant().getCountry() == null
                        ? null
                        : tx.getMerchant().getCountry().getCountryCode(),

                tx.getIssuerBank() == null || tx.getIssuerBank().getCountry() == null
                        ? null
                        : tx.getIssuerBank().getCountry().getCountryCode(),

                tx.getRegion() == null ? null : tx.getRegion().getRegionCode(),

                tx.getCard() == null || tx.getCard().getCardType() == null
                        ? null
                        : tx.getCard().getCardType().getCardTypeName(),

                tx.getCardNetwork() == null
                        ? null
                        : tx.getCardNetwork().getNetworkCode(),

                deriveCardPresence(tx.getTransactionChannel()),

                mapChannel(tx.getTransactionChannel()),

                tx.getMerchant() == null || tx.getMerchant().getMcc() == null
                        ? null
                        : tx.getMerchant().getMcc().getMccCode(),

                "Y".equalsIgnoreCase(tx.getIs3dsAuthenticated()),

                tx.getEciValue(),

                tx.getAuthorizationDatetime(),
                tx.getClearingDatetime()
        );
    }

    private String mapChannel(Transaction.TransactionChannel channel) {
        if (channel == null) return null;

        return switch (channel) {
            case ECOMMERCE -> "ecommerce";
            case POS -> "pos";
            case MOTO -> "moto";
            case CONTACTLESS -> "pos";
        };
    }

    private String deriveCardPresence(Transaction.TransactionChannel channel) {
        if (channel == null) return null;

        return switch (channel) {
            case ECOMMERCE, MOTO -> "card_not_present";
            case POS, CONTACTLESS -> "card_present";
        };
    }
}