package com.example.api.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "transactions")
public class Transaction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "transaction_id")
    private Long transactionId;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "client_id", nullable = false, foreignKey = @ForeignKey(name = "fk_transactions_client"))
    private Client client;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "merchant_id", nullable = false, foreignKey = @ForeignKey(name = "fk_transactions_merchant"))
    private Merchant merchant;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "card_id", nullable = false, foreignKey = @ForeignKey(name = "fk_transactions_card"))
    private Card card;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "acquiring_partner_id", nullable = false, foreignKey = @ForeignKey(name = "fk_transactions_acquiring_partner"))
    private AcquiringPartner acquiringPartner;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "issuer_bank_id", nullable = false, foreignKey = @ForeignKey(name = "fk_transactions_issuer_bank"))
    private Bank issuerBank;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "card_network_id", nullable = false, foreignKey = @ForeignKey(name = "fk_transactions_card_network"))
    private CardNetwork cardNetwork;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "mcc_code", nullable = false, foreignKey = @ForeignKey(name = "fk_transactions_mcc_code"))
    private MccCode mccCode;

    @NotNull @DecimalMin(value = "0.01")
    @Column(name = "transaction_amount", precision = 12, scale = 2, nullable = false)
    private BigDecimal transactionAmount;

    @NotBlank @Size(min = 3, max = 3)
    @JdbcTypeCode(SqlTypes.CHAR)
    @Column(name = "transaction_currency", columnDefinition = "CHAR(3)", nullable = false)
    private String transactionCurrency;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_channel", length = 30, nullable = false)
    private TransactionChannel transactionChannel;

    @NotNull
    @Column(name = "authorization_datetime", nullable = false)
    private LocalDateTime authorizationDatetime;

    @Column(name = "clearing_datetime")
    private LocalDateTime clearingDatetime;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_status", length = 30, nullable = false)
    private TransactionStatus transactionStatus;

    @NotBlank @Pattern(regexp = "^[YN]$")
    @JdbcTypeCode(SqlTypes.CHAR)
    @Column(name = "is_3ds_authenticated", columnDefinition = "CHAR(1)", nullable = false)
    @Builder.Default
    private String is3dsAuthenticated = "N";

    @Column(name = "eci_value", length = 2)
    private String eciValue;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "region_code", nullable = false, foreignKey = @ForeignKey(name = "fk_transactions_region"))
    private Region region;

    public enum TransactionChannel { ECOMMERCE, POS, MOTO, CONTACTLESS }
    public enum TransactionStatus { APPROVED, DECLINED, SETTLED }
}
