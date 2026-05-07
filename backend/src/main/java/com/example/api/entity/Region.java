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
@Table(name = "regions", uniqueConstraints = @UniqueConstraint(name = "uq_regions_name", columnNames = "region_name"))
public class Region {
    @Id
    @Column(name = "region_code", length = 30, nullable = false)
    private String regionCode;

    @NotBlank
    @Column(name = "region_name", length = 100, nullable = false)
    private String regionName;

    @Column(name = "description", length = 255)
    private String description;
}
