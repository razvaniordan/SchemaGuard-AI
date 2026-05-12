package com.example.api.dto.request;

import com.example.api.entity.Transaction.TransactionChannel;
import com.example.api.entity.Transaction.TransactionStatus;
import jakarta.validation.constraints.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record TransactionRequest(
        @NotNull Long clientId,
        @NotNull Long merchantId,
        @NotNull Long cardId,
        @NotNull Long acquiringPartnerId,
        @NotNull Long issuerBankId,
        @NotNull Long cardNetworkId,
        @NotBlank String regionCode,

        @NotNull
        @DecimalMin("0.01")
        BigDecimal transactionAmount,

        @NotBlank
        @Size(min = 3, max = 3)
        String transactionCurrency,

        @NotNull
        TransactionChannel transactionChannel,

        @NotNull
        LocalDateTime authorizationDatetime,

        LocalDateTime clearingDatetime,

        @NotBlank(message = "MCC code is required")
        @Pattern(regexp = "^[0-9]{4}$", message = "MCC code must be exactly 4 digits")
        String mccCode,
        
        @NotNull
        TransactionStatus transactionStatus,

        @Pattern(regexp = "^[YN]$")
        String is3dsAuthenticated,

        @Size(max = 2)
        String eciValue

) {}