package com.example.api.dto;

import java.math.BigDecimal;
import java.util.List;

public class ClassificationResult {

    private String category;
    private BigDecimal confidence;
    private List<String> matchedConditions;

    public ClassificationResult() {
    }

    public ClassificationResult(
            String category,
            BigDecimal confidence,
            List<String> matchedConditions
    ) {
        this.category = category;
        this.confidence = confidence;
        this.matchedConditions = matchedConditions;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public BigDecimal getConfidence() {
        return confidence;
    }

    public void setConfidence(BigDecimal confidence) {
        this.confidence = confidence;
    }

    public List<String> getMatchedConditions() {
        return matchedConditions;
    }

    public void setMatchedConditions(List<String> matchedConditions) {
        this.matchedConditions = matchedConditions;
    }
}
