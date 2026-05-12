package com.example.api.repository;

import com.example.api.entity.MccCode;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface MccCodeRepository extends JpaRepository<MccCode, String> {
    Optional<MccCode> findByMccCode(String mccCode);
}
