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
@Table(name = "cards")
public class Card {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "card_id")
    private Long cardId;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "client_id", nullable = false, foreignKey = @ForeignKey(name = "fk_cards_client"))
    private Client client;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "issuer_bank_id", nullable = false, foreignKey = @ForeignKey(name = "fk_cards_issuer_bank"))
    private Bank issuerBank;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "card_network_id", nullable = false, foreignKey = @ForeignKey(name = "fk_cards_network"))
    private CardNetwork cardNetwork;

    @NotNull
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "card_type_id", nullable = false, foreignKey = @ForeignKey(name = "fk_cards_card_type"))
    private CardType cardType;

    @Column(name = "card_product_type", length = 30)
    private String cardProductType;
}
