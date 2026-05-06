package com.example.api.repository;

import com.example.api.entity.TransactionSimulation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TransactionSimulationRepository extends JpaRepository<TransactionSimulation, Long> {
}
