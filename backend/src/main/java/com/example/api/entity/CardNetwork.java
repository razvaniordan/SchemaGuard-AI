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
@Table(name = "card_networks", uniqueConstraints = {
        @UniqueConstraint(name = "uq_card_networks_code", columnNames = "network_code"),
        @UniqueConstraint(name = "uq_card_networks_name", columnNames = "network_name")
})
public class CardNetwork {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "card_network_id")
    private Long cardNetworkId;

    @NotBlank
    @Column(name = "network_code", length = 30, nullable = false)
    private String networkCode;

    @NotBlank
    @Column(name = "network_name", length = 100, nullable = false)
    private String networkName;
}
