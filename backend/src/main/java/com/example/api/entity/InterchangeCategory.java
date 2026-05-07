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
@Table(name = "interchange_categories", uniqueConstraints = @UniqueConstraint(name = "uq_interchange_categories_name", columnNames = "category_name"))
public class InterchangeCategory {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "category_id")
    private Long categoryId;

    @NotBlank
    @Column(name = "category_name", length = 100, nullable = false)
    private String categoryName;

    @Column(name = "description", length = 255)
    private String description;
}
