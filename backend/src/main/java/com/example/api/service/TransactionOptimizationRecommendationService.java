package com.example.api.service;

import com.example.api.dto.request.TransactionOptimizationRecommendationRequest;
import com.example.api.dto.response.TransactionOptimizationRecommendationResponse;
import com.example.api.entity.Transaction;
import com.example.api.entity.TransactionOptimizationRecommendation;
import com.example.api.repository.TransactionOptimizationRecommendationRepository;
import com.example.api.repository.TransactionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class TransactionOptimizationRecommendationService {
    private final TransactionOptimizationRecommendationRepository recommendationRepository;
    private final TransactionRepository transactionRepository;

    public TransactionOptimizationRecommendationService(TransactionOptimizationRecommendationRepository recommendationRepository,
                                                        TransactionRepository transactionRepository) {
        this.recommendationRepository = recommendationRepository;
        this.transactionRepository = transactionRepository;
    }

    @Transactional(readOnly = true)
    public List<TransactionOptimizationRecommendationResponse> findAll() {
        return recommendationRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public TransactionOptimizationRecommendationResponse create(TransactionOptimizationRecommendationRequest request) {
        Transaction transaction = transactionRepository.findById(request.transactionId())
                .orElseThrow(() -> new IllegalArgumentException("Transaction not found: " + request.transactionId()));
        TransactionOptimizationRecommendation recommendation = TransactionOptimizationRecommendation.builder()
                .transaction(transaction)
                .recommendationType(request.recommendationType())
                .recommendationText(request.recommendationText())
                .currentValue(request.currentValue())
                .recommendedValue(request.recommendedValue())
                .impactDescription(request.impactDescription())
                .estimatedSavingAmount(request.estimatedSavingAmount())
                .estimatedSavingPercentage(request.estimatedSavingPercentage())
                .priorityRank(request.priorityRank())
                .build();
        return toResponse(recommendationRepository.save(recommendation));
    }

    private TransactionOptimizationRecommendationResponse toResponse(TransactionOptimizationRecommendation recommendation) {
        return new TransactionOptimizationRecommendationResponse(
                recommendation.getRecommendationId(),
                recommendation.getTransaction().getTransactionId(),
                recommendation.getRecommendationType(),
                recommendation.getRecommendationText(),
                recommendation.getCurrentValue(),
                recommendation.getRecommendedValue(),
                recommendation.getImpactDescription(),
                recommendation.getEstimatedSavingAmount(),
                recommendation.getEstimatedSavingPercentage(),
                recommendation.getPriorityRank(),
                recommendation.getCreatedAt()
        );
    }
}
