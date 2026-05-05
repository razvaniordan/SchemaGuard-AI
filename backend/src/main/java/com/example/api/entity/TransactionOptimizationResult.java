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
@Table(name = "transaction_optimization_results", uniqueConstraints = @UniqueConstraint(name = "uq_optimization_transaction", columnNames = "transaction_id"), indexes = {
        @Index(name = "idx_optimization_current_result", columnList = "current_result_id"),
        @Index(name = "idx_optimization_optimal_result", columnList = "optimal_result_id")
})
public class TransactionOptimizationResult {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "optimization_result_id")
    private Long optimizationResultId;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "transaction_id", nullable = false, foreignKey = @ForeignKey(name = "fk_optimization_transaction"))
    private Transaction transaction;

    @NotNull @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "current_result_id", nullable = false, foreignKey = @ForeignKey(name = "fk_optimization_current_result"))
    private TransactionInterchangeResult currentResult;

    @NotNull @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "optimal_result_id", nullable = false, foreignKey = @ForeignKey(name = "fk_optimization_optimal_result"))
    private TransactionInterchangeResult optimalResult;

    @NotNull @DecimalMin("0.00")
    @Column(name = "current_fee_amount", precision = 12, scale = 2, nullable = false)
    private BigDecimal currentFeeAmount;

    @NotNull @DecimalMin("0.00")
    @Column(name = "optimal_fee_amount", precision = 12, scale = 2, nullable = false)
    private BigDecimal optimalFeeAmount;

    @NotNull @DecimalMin("0.00")
    @Column(name = "saving_amount", precision = 12, scale = 2, nullable = false)
    private BigDecimal savingAmount;

    @DecimalMin("0.0000")
    @Column(name = "saving_percentage", precision = 7, scale = 4)
    private BigDecimal savingPercentage;

    @NotNull
    @Column(name = "created_at", nullable = false)
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
}
