package com.example.api.ml.dto;

import java.math.BigDecimal;

public record PythonTransactionInput(

        String transactionId,

        String merchantId,

        String cardId,

        BigDecimal amount,

        String currency,

        String merchantCountry,

        String issuerCountry,

        String region,

        String cardType,

        String cardBrand,

        String cardPresence,

        String channel,

        String mcc,

        Boolean threeDS,

        String eci,

        String authDate,

        String clearingDate,

        Long clearingDelayDays

) {}