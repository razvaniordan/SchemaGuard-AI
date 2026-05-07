package com.example.api.dto.request;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record PythonClassificationRequest(String transactionId,
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

                                          LocalDateTime authDate,
                                          LocalDateTime clearingDate) {}
