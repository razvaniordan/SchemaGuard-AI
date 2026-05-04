package com.example.api.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "transactions")
public class Transaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @DecimalMin("0.01")
    private BigDecimal amount;

    @NotBlank
    private String currency;

    @NotBlank
    private String country;

    @NotBlank
    private String cardType;

    @NotBlank
    private String channel;

    @NotBlank
    private String mcc;

    @NotNull
    private Boolean threeDS;

    @NotNull
    private LocalDate authDate;

    @NotNull
    private LocalDate clearingDate;

    @NotBlank
    private String cardBrand;

    @NotBlank
    private String cardPresence;

    @NotBlank
    private String transactionType;

    public Transaction() {
    }

    public Transaction(
            BigDecimal amount,
            String currency,
            String country,
            String cardType,
            String channel,
            String mcc,
            Boolean threeDS,
            LocalDate authDate,
            LocalDate clearingDate,
            String cardBrand,
            String cardPresence,
            String transactionType
    ) {
        this.amount = amount;
        this.currency = currency;
        this.country = country;
        this.cardType = cardType;
        this.channel = channel;
        this.mcc = mcc;
        this.threeDS = threeDS;
        this.authDate = authDate;
        this.clearingDate = clearingDate;
        this.cardBrand = cardBrand;
        this.cardPresence = cardPresence;
        this.transactionType = transactionType;
    }

    public Long getId() {
        return id;
    }

    public BigDecimal getAmount() {
        return amount;
    }

    public void setAmount(BigDecimal amount) {
        this.amount = amount;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
    }

    public String getCardType() {
        return cardType;
    }

    public void setCardType(String cardType) {
        this.cardType = cardType;
    }

    public String getChannel() {
        return channel;
    }

    public void setChannel(String channel) {
        this.channel = channel;
    }

    public String getMcc() {
        return mcc;
    }

    public void setMcc(String mcc) {
        this.mcc = mcc;
    }

    public Boolean getThreeDS() {
        return threeDS;
    }

    public void setThreeDS(Boolean threeDS) {
        this.threeDS = threeDS;
    }

    public LocalDate getAuthDate() {
        return authDate;
    }

    public void setAuthDate(LocalDate authDate) {
        this.authDate = authDate;
    }

    public LocalDate getClearingDate() {
        return clearingDate;
    }

    public void setClearingDate(LocalDate clearingDate) {
        this.clearingDate = clearingDate;
    }

    public String getCardBrand() {
        return cardBrand;
    }

    public void setCardBrand(String cardBrand) {
        this.cardBrand = cardBrand;
    }

    public String getCardPresence() {
        return cardPresence;
    }

    public void setCardPresence(String cardPresence) {
        this.cardPresence = cardPresence;
    }

    public String getTransactionType() {
        return transactionType;
    }

    public void setTransactionType(String transactionType) {
        this.transactionType = transactionType;
    }
}