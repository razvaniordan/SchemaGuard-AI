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
@Table(name = "clients")
public class Client {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "client_id")
    private Long clientId;

    @NotBlank
    @Column(name = "client_name", length = 100, nullable = false)
    private String clientName;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JdbcTypeCode(SqlTypes.CHAR)
    @JoinColumn(name = "country_code", nullable = false, columnDefinition = "CHAR(2)", foreignKey = @ForeignKey(name = "fk_clients_country"))
    private Country country;
}
