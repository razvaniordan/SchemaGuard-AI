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
@Table(name = "countries", uniqueConstraints = @UniqueConstraint(name = "uq_countries_name", columnNames = "country_name"))
public class Country {
    @Id
    @Pattern(regexp = "^[A-Z]{2}$")
    @JdbcTypeCode(SqlTypes.CHAR)
    @Column(name = "country_code", columnDefinition = "CHAR(2)", nullable = false)
    private String countryCode;

    @NotBlank
    @Column(name = "country_name", length = 100, nullable = false)
    private String countryName;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "region_code", nullable = false, foreignKey = @ForeignKey(name = "fk_countries_region"))
    private Region region;
}
