package com.example.api.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "transaction_optimization_recommendations", uniqueConstraints = {
        @UniqueConstraint(name = "uq_txn_recommendation_type", columnNames = {"transaction_id", "recommendation_type"}),
        @UniqueConstraint(name = "uq_txn_recommendation_rank", columnNames = {"transaction_id", "priority_rank"})
}, indexes = @Index(name = "idx_txn_recommendations_transaction", columnList = "transaction_id"))
public class TransactionOptimizationRecommendation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "recommendation_id")
    private Long recommendationId;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "transaction_id", nullable = false, foreignKey = @ForeignKey(name = "fk_txn_recommendation_transaction"))
    private Transaction transaction;

    @NotBlank
    @Column(name = "recommendation_type", length = 50, nullable = false)
    private String recommendationType;

    @NotBlank
    @Column(name = "recommendation_text", length = 500, nullable = false)
    private String recommendationText;

    @Column(name = "current_value", length = 100)
    private String currentValue;

    @Column(name = "recommended_value", length = 100)
    private String recommendedValue;

    @Column(name = "impact_description", length = 500)
    private String impactDescription;

    @DecimalMin("0.00")
    @Column(name = "estimated_saving_amount", precision = 12, scale = 2)
    private BigDecimal estimatedSavingAmount;

    @DecimalMin("0.0000")
    @Column(name = "estimated_saving_percentage", precision = 7, scale = 4)
    private BigDecimal estimatedSavingPercentage;

    @NotNull @Min(1)
    @Column(name = "priority_rank", nullable = false)
    private Long priorityRank;

    @NotNull
    @Column(name = "created_at", nullable = false)
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
}
