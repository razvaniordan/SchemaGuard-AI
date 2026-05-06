package com.example.api.repository;

import com.example.api.entity.TransactionOptimizationResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TransactionOptimizationResultRepository extends JpaRepository<TransactionOptimizationResult, Long> {
}
