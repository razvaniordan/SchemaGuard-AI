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
@Table(name = "mcc_codes")
public class MccCode {
    @Id
    @Pattern(regexp = "^[0-9]{4}$")
    @Column(name = "mcc_code", length = 4, nullable = false)
    private String mccCode;

    @NotBlank
    @Column(name = "mcc_description", length = 255, nullable = false)
    private String mccDescription;
}
