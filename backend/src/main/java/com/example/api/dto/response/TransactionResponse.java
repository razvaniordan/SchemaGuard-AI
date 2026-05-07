package com.example.api.dto.response;

import com.example.api.entity.Transaction.TransactionChannel;
import com.example.api.entity.Transaction.TransactionStatus;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record TransactionResponse(
        Long transactionId,

        Long clientId,
        String clientName,

        Long merchantId,
        String merchantName,
        String mccCode,

        Long cardId,
        Long acquiringPartnerId,
        Long issuerBankId,
        Long cardNetworkId,

        BigDecimal transactionAmount,
        String transactionCurrency,
        TransactionChannel transactionChannel,

        LocalDateTime authorizationDatetime,
        LocalDateTime clearingDatetime,

        TransactionStatus transactionStatus,
        String is3dsAuthenticated,
        String eciValue,

        String regionCode
) {}