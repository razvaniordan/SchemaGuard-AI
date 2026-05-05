package com.example.api.repository;

import com.example.api.entity.InterchangeRule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface InterchangeRuleRepository extends JpaRepository<InterchangeRule, Long> {
}
