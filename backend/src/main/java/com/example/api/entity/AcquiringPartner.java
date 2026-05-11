package com.example.api.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "acquiring_partners", uniqueConstraints = @UniqueConstraint(name = "uq_acquiring_partner_name_country", columnNames = {"partner_name", "country_code"}))
public class AcquiringPartner {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "acquiring_partner_id")
    private Long acquiringPartnerId;

    @NotBlank
    @Column(name = "partner_name", length = 100, nullable = false)
    private String partnerName;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "partner_type", length = 30, nullable = false)
    private PartnerType partnerType;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JdbcTypeCode(SqlTypes.CHAR)
    @JoinColumn(name = "country_code", nullable = false, columnDefinition = "CHAR(2)", foreignKey = @ForeignKey(name = "fk_acquiring_partners_country"))
    private Country country;

    public enum PartnerType { BANK, PSP }
}
