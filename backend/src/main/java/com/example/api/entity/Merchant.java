package com.example.api.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "merchants")
public class Merchant {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "merchant_id")
    private Long merchantId;

    @NotBlank
    @Column(name = "merchant_name", length = 150, nullable = false)
    private String merchantName;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "mcc_code", nullable = false, foreignKey = @ForeignKey(name = "fk_merchants_mcc"))
    private MccCode mcc;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "country_code", nullable = false, foreignKey = @ForeignKey(name = "fk_merchants_country"))
    private Country country;

    @NotBlank
    @Column(name = "city", length = 100, nullable = false)
    private String city;

    @NotBlank
    @Column(name = "address", length = 255, nullable = false)
    private String address;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "acquiring_partner_id", nullable = false, foreignKey = @ForeignKey(name = "fk_merchants_acquiring_partner"))
    private AcquiringPartner acquiringPartner;
}
