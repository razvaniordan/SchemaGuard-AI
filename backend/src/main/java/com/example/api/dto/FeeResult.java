package com.example.api.dto;

import java.math.BigDecimal;

public class FeeResult {

    private String classification;
    private BigDecimal feeRate;
    private BigDecimal feeAmount;
    private String calculationMethod;

    public FeeResult() {
    }

    public FeeResult(
            String classification,
            BigDecimal feeRate,
            BigDecimal feeAmount,
            String calculationMethod
    ) {
        this.classification = classification;
        this.feeRate = feeRate;
        this.feeAmount = feeAmount;
        this.calculationMethod = calculationMethod;
    }

    public String getClassification() {
        return classification;
    }

    public void setClassification(String classification) {
        this.classification = classification;
    }

    public BigDecimal getFeeRate() {
        return feeRate;
    }

    public void setFeeRate(BigDecimal feeRate) {
        this.feeRate = feeRate;
    }

    public BigDecimal getFeeAmount() {
        return feeAmount;
    }

    public void setFeeAmount(BigDecimal feeAmount) {
        this.feeAmount = feeAmount;
    }

    public String getCalculationMethod() {
        return calculationMethod;
    }

    public void setCalculationMethod(String calculationMethod) {
        this.calculationMethod = calculationMethod;
    }
}
