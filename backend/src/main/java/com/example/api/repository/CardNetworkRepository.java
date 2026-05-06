package com.example.api.repository;

import com.example.api.entity.CardNetwork;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CardNetworkRepository extends JpaRepository<CardNetwork, Long> {
}
