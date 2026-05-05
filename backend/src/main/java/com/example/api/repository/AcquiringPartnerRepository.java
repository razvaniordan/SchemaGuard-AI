package com.example.api.repository;

import com.example.api.entity.AcquiringPartner;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AcquiringPartnerRepository extends JpaRepository<AcquiringPartner, Long> {
}
