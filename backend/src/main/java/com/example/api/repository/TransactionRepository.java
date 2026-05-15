package com.example.api.repository;

import com.example.api.entity.Transaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.springframework.data.jpa.repository.EntityGraph;

import java.util.List;

@Repository
public interface TransactionRepository
        extends JpaRepository<Transaction, Long> {

    @Override
    @EntityGraph(attributePaths = {
            "merchant",
            "merchant.country",
            "card",
            "card.cardType",
            "issuerBank",
            "issuerBank.country",
            "cardNetwork",
            "mccCode",
            "region"
    })
    List<Transaction> findAll();
}
