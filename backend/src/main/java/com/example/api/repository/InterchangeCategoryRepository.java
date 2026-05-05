package com.example.api.repository;

import com.example.api.entity.InterchangeCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface InterchangeCategoryRepository extends JpaRepository<InterchangeCategory, Long> {
}
