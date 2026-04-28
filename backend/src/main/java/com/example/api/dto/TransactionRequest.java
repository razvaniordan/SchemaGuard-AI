package com.example.api.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

public record TransactionRequest(
        @NotBlank(message = "merchantName is required") String merchantName,
        @NotBlank(message = "mcc is required") String mcc,
        @NotNull(message = "amount is required") @DecimalMin(value = "0.01") BigDecimal amount,
        @NotBlank(message = "currency is required") String currency
) {}
