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
@Table(name = "card_types", uniqueConstraints = @UniqueConstraint(name = "uq_card_types_name", columnNames = "card_type_name"))
public class CardType {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "card_type_id")
    private Long cardTypeId;

    @NotBlank
    @Column(name = "card_type_name", length = 30, nullable = false)
    private String cardTypeName;

    @Column(name = "description", length = 255)
    private String description;
}
