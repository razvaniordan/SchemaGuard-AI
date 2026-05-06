package com.example.api.repository;

import com.example.api.entity.TransactionOptimizationRecommendation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TransactionOptimizationRecommendationRepository extends JpaRepository<TransactionOptimizationRecommendation, Long> {
}
