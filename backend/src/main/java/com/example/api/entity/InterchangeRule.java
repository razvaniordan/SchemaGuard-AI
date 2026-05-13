package com.example.api.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "interchange_rules")
public class InterchangeRule {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "rule_id")
    private Long ruleId;

    @NotNull
    @Min(1)
    @Column(name = "rule_priority", nullable = false)
    private Long rulePriority;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "card_network_id")
    private CardNetwork cardNetwork;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "mcc_code")
    private MccCode mcc;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "card_type_id")
    private CardType cardType;

    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_channel", length = 30)
    private Transaction.TransactionChannel transactionChannel;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "region_code")
    private Region region;

    @Pattern(regexp = "^[YN]$")
    @JdbcTypeCode(SqlTypes.CHAR)
    @Column(name = "is_3ds_required", columnDefinition = "CHAR(1)")
    private String is3dsRequired;

    @Enumerated(EnumType.STRING)
    @Column(name = "clearing_time_condition", length = 30)
    private ClearingTimeCondition clearingTimeCondition;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "category_id", nullable = false)
    private InterchangeCategory category;

    @NotNull
    @DecimalMin("0.0000")
    @Column(name = "fee_percentage", precision = 7, scale = 4, nullable = false)
    private BigDecimal feePercentage;

    @NotNull
    @DecimalMin("0.00")
    @Column(name = "fixed_fee_amount", precision = 12, scale = 2, nullable = false)
    @Builder.Default
    private BigDecimal fixedFeeAmount = BigDecimal.ZERO;

    @NotBlank
    @Size(min = 3, max = 3)
    @JdbcTypeCode(SqlTypes.CHAR)
    @Column(name = "currency_code", nullable = false, columnDefinition = "CHAR(3)")
    @Builder.Default
    private String currencyCode = "EUR";

    public enum ClearingTimeCondition {
        LTE_24H,
        GT_24H
    }
}