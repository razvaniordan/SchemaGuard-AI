package com.example.api.service;

import com.example.api.dto.request.InterchangeCategoryRequest;
import com.example.api.dto.response.InterchangeCategoryResponse;
import com.example.api.entity.InterchangeCategory;
import com.example.api.repository.InterchangeCategoryRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class InterchangeCategoryService {
    private final InterchangeCategoryRepository interchangeCategoryRepository;

    public InterchangeCategoryService(InterchangeCategoryRepository interchangeCategoryRepository) {
        this.interchangeCategoryRepository = interchangeCategoryRepository;
    }

    @Transactional(readOnly = true)
    public List<InterchangeCategoryResponse> findAll() {
        return interchangeCategoryRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public InterchangeCategoryResponse create(InterchangeCategoryRequest request) {
        InterchangeCategory interchangeCategory = InterchangeCategory.builder()
                .categoryName(request.categoryName())
                .description(request.description())
                .build();
        return toResponse(interchangeCategoryRepository.save(interchangeCategory));
    }

    private InterchangeCategoryResponse toResponse(InterchangeCategory interchangeCategory) {
        return new InterchangeCategoryResponse(interchangeCategory.getCategoryId(), interchangeCategory.getCategoryName(), interchangeCategory.getDescription());
    }
}
