package com.example.api.dto;

import java.math.BigDecimal;
import java.time.Instant;

public record TransactionResponse(
        String id,
        String merchantName,
        String mcc,
        BigDecimal amount,
        String currency,
        Instant createdAt
) {}
