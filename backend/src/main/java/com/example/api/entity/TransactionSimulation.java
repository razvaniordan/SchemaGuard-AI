package com.example.api.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "transaction_simulations")
public class TransactionSimulation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "simulation_id")
    private Long simulationId;

    @NotNull @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "transaction_id", nullable = false, foreignKey = @ForeignKey(name = "fk_transaction_simulations_transaction"))
    private Transaction transaction;

    @Pattern(regexp = "^[YN]$")
    @Column(name = "simulated_is_3ds_authenticated", length = 1)
    private String simulatedIs3dsAuthenticated;

    @Column(name = "simulated_eci_value", length = 2)
    private String simulatedEciValue;

    @Column(name = "simulated_clearing_datetime")
    private LocalDateTime simulatedClearingDatetime;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "simulated_region_code", foreignKey = @ForeignKey(name = "fk_simulations_region"))
    private Region simulatedRegion;

    @Column(name = "simulation_reason", length = 500)
    private String simulationReason;

    @NotNull
    @Column(name = "created_at", nullable = false)
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
}
