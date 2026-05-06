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
@Table(name = "transaction_interchange_results", uniqueConstraints = @UniqueConstraint(name = "uq_txn_interchange_result_type", columnNames = {"transaction_id", "result_type"}))
public class TransactionInterchangeResult {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "result_id")
    private Long resultId;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "transaction_id", nullable = false, foreignKey = @ForeignKey(name = "fk_txn_interchange_result_transaction"))
    private Transaction transaction;

    @NotNull @Enumerated(EnumType.STRING)
    @Column(name = "result_type", length = 30, nullable = false)
    private ResultType resultType;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "category_id", nullable = false, foreignKey = @ForeignKey(name = "fk_txn_interchange_result_category"))
    private InterchangeCategory category;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "applied_rule_id", foreignKey = @ForeignKey(name = "fk_txn_interchange_result_rule"))
    private InterchangeRule appliedRule;

    @NotNull @DecimalMin("0.0000")
    @Column(name = "fee_percentage", precision = 7, scale = 4, nullable = false)
    private BigDecimal feePercentage;

    @NotNull @DecimalMin("0.00")
    @Column(name = "fixed_fee_amount", precision = 12, scale = 2, nullable = false)
    @Builder.Default
    private BigDecimal fixedFeeAmount = BigDecimal.ZERO;

    @NotNull @DecimalMin("0.00")
    @Column(name = "interchange_fee_amount", precision = 12, scale = 2, nullable = false)
    private BigDecimal interchangeFeeAmount;

    @NotNull
    @Column(name = "evaluated_at", nullable = false)
    @Builder.Default
    private LocalDateTime evaluatedAt = LocalDateTime.now();

    public enum ResultType { CURRENT, OPTIMAL }
}
