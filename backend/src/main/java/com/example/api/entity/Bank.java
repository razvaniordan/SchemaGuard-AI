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
@Table(name = "banks", uniqueConstraints = @UniqueConstraint(name = "uq_banks_name_country", columnNames = {"bank_name", "country_code"}))
public class Bank {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "bank_id")
    private Long bankId;

    @NotBlank
    @Column(name = "bank_name", length = 100, nullable = false)
    private String bankName;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "country_code", nullable = false, foreignKey = @ForeignKey(name = "fk_banks_country"))
    private Country country;
}
