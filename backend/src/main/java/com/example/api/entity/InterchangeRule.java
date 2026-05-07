package com.example.api.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "interchange_rules", uniqueConstraints = {
        @UniqueConstraint(name = "uq_interchange_rules_priority", columnNames = "rule_priority"),
        @UniqueConstraint(name = "uq_interchange_rules_scope", columnNames = {
                "card_network_id", "mcc_code", "card_type_id", "transaction_channel",
                "region_code", "is_3ds_required", "clearing_time_condition"
        })
})
public class InterchangeRule {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "rule_id")
    private Long ruleId;

    @NotNull @Min(1)
    @Column(name = "rule_priority", nullable = false)
    private Integer rulePriority;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "card_network_id", foreignKey = @ForeignKey(name = "fk_interchange_rules_network"))
    private CardNetwork cardNetwork;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "mcc_code", foreignKey = @ForeignKey(name = "fk_interchange_rules_mcc"))
    private MccCode mcc;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "card_type_id", foreignKey = @ForeignKey(name = "fk_interchange_rules_card_type"))
    private CardType cardType;

    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_channel", length = 30)
    private Transaction.TransactionChannel transactionChannel;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "region_code", foreignKey = @ForeignKey(name = "fk_interchange_rules_region"))
    private Region region;

    @Pattern(regexp = "^[YN]$")
    @Column(name = "is_3ds_required", length = 1)
    private String is3dsRequired;

    @Enumerated(EnumType.STRING)
    @Column(name = "clearing_time_condition", length = 30)
    private ClearingTimeCondition clearingTimeCondition;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "category_id", nullable = false, foreignKey = @ForeignKey(name = "fk_interchange_rules_category"))
    private InterchangeCategory category;

    @NotNull @DecimalMin("0.0000")
    @Column(name = "fee_percentage", precision = 7, scale = 4, nullable = false)
    private BigDecimal feePercentage;

    @NotNull @DecimalMin("0.00")
    @Column(name = "fixed_fee_amount", precision = 12, scale = 2, nullable = false)
    @Builder.Default
    private BigDecimal fixedFeeAmount = BigDecimal.ZERO;

    @NotBlank @Size(min = 3, max = 3)
    @Column(name = "currency_code", length = 3, nullable = false)
    @Builder.Default
    private String currencyCode = "EUR";

    public enum ClearingTimeCondition { LTE_24H, GT_24H, ANY }
}
