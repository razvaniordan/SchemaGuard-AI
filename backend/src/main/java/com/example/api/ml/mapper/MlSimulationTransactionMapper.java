package com.example.api.ml.mapper;

import com.example.api.entity.Transaction;
import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class MlSimulationTransactionMapper {

    public Transaction toSimulatedTransaction(
            Transaction original,
            JsonNode simulatedTransaction
    ) {
        if (original == null) {
            throw new IllegalArgumentException("Original transaction must not be null");
        }

        Transaction simulated = cloneTransaction(original);

        if (simulatedTransaction == null || simulatedTransaction.isNull()) {
            return simulated;
        }

        applyThreeDs(simulated, simulatedTransaction);
        applyClearingDate(simulated, simulatedTransaction);
        applyChannel(simulated, simulatedTransaction);

        return simulated;
    }

    private Transaction cloneTransaction(Transaction original) {
        Transaction clone = new Transaction();

        clone.setTransactionId(original.getTransactionId());
        clone.setClient(original.getClient());
        clone.setMerchant(original.getMerchant());
        clone.setCard(original.getCard());
        clone.setAcquiringPartner(original.getAcquiringPartner());
        clone.setIssuerBank(original.getIssuerBank());
        clone.setCardNetwork(original.getCardNetwork());
        clone.setTransactionAmount(original.getTransactionAmount());
        clone.setTransactionCurrency(original.getTransactionCurrency());
        clone.setTransactionChannel(original.getTransactionChannel());
        clone.setAuthorizationDatetime(original.getAuthorizationDatetime());
        clone.setClearingDatetime(original.getClearingDatetime());
        clone.setTransactionStatus(original.getTransactionStatus());
        clone.setRegion(original.getRegion());
        clone.setIs3dsAuthenticated(original.getIs3dsAuthenticated());
        clone.setEciValue(original.getEciValue());

        return clone;
    }

    private void applyThreeDs(Transaction simulated, JsonNode node) {
        if (!node.hasNonNull("threeDS")) {
            return;
        }

        boolean threeDs = node.get("threeDS").asBoolean();

        simulated.setIs3dsAuthenticated(threeDs ? "Y" : "N");

        if (threeDs) {
            simulated.setEciValue("05");
        } else {
            simulated.setEciValue("07");
        }
    }

    private void applyClearingDate(Transaction simulated, JsonNode node) {
        if (!node.hasNonNull("clearingDate")) {
            return;
        }

        String clearingDate = node.get("clearingDate").asText();

        // Temporary guard because Python currently returns clearingDate: 0
        if ("0".equals(clearingDate)) {
            return;
        }

        simulated.setClearingDatetime(LocalDateTime.parse(clearingDate));
    }

    private void applyChannel(Transaction simulated, JsonNode node) {
        if (!node.hasNonNull("channel")) {
            return;
        }

        String channel = node.get("channel").asText();

        switch (channel) {
            case "eCommerce" -> simulated.setTransactionChannel(Transaction.TransactionChannel.ECOMMERCE);
            case "POS" -> simulated.setTransactionChannel(Transaction.TransactionChannel.POS);
            case "MOTO" -> simulated.setTransactionChannel(Transaction.TransactionChannel.MOTO);
            case "CONTACTLESS" -> simulated.setTransactionChannel(Transaction.TransactionChannel.CONTACTLESS);
            default -> {
                // Keep original channel if ML returns unknown value.
            }
        }
    }
}