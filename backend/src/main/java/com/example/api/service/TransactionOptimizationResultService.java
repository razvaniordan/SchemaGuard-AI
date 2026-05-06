package com.example.api.service;

import com.example.api.dto.request.TransactionOptimizationResultRequest;
import com.example.api.dto.response.TransactionOptimizationResultResponse;
import com.example.api.entity.Transaction;
import com.example.api.entity.TransactionInterchangeResult;
import com.example.api.entity.TransactionOptimizationResult;
import com.example.api.repository.TransactionInterchangeResultRepository;
import com.example.api.repository.TransactionOptimizationResultRepository;
import com.example.api.repository.TransactionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class TransactionOptimizationResultService {
    private final TransactionOptimizationResultRepository optimizationResultRepository;
    private final TransactionRepository transactionRepository;
    private final TransactionInterchangeResultRepository interchangeResultRepository;

    public TransactionOptimizationResultService(TransactionOptimizationResultRepository optimizationResultRepository,
                                                TransactionRepository transactionRepository,
                                                TransactionInterchangeResultRepository interchangeResultRepository) {
        this.optimizationResultRepository = optimizationResultRepository;
        this.transactionRepository = transactionRepository;
        this.interchangeResultRepository = interchangeResultRepository;
    }

    @Transactional(readOnly = true)
    public List<TransactionOptimizationResultResponse> findAll() {
        return optimizationResultRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public TransactionOptimizationResultResponse create(TransactionOptimizationResultRequest request) {
        Transaction transaction = transactionRepository.findById(request.transactionId())
                .orElseThrow(() -> new IllegalArgumentException("Transaction not found: " + request.transactionId()));
        TransactionInterchangeResult currentResult = interchangeResultRepository.findById(request.currentResultId())
                .orElseThrow(() -> new IllegalArgumentException("Current interchange result not found: " + request.currentResultId()));
        TransactionInterchangeResult optimalResult = interchangeResultRepository.findById(request.optimalResultId())
                .orElseThrow(() -> new IllegalArgumentException("Optimal interchange result not found: " + request.optimalResultId()));

        TransactionOptimizationResult result = TransactionOptimizationResult.builder()
                .transaction(transaction)
                .currentResult(currentResult)
                .optimalResult(optimalResult)
                .currentFeeAmount(request.currentFeeAmount())
                .optimalFeeAmount(request.optimalFeeAmount())
                .savingAmount(request.savingAmount())
                .savingPercentage(request.savingPercentage())
                .build();
        return toResponse(optimizationResultRepository.save(result));
    }

    private TransactionOptimizationResultResponse toResponse(TransactionOptimizationResult result) {
        return new TransactionOptimizationResultResponse(
                result.getOptimizationResultId(),
                result.getTransaction().getTransactionId(),
                result.getCurrentResult().getResultId(),
                result.getOptimalResult().getResultId(),
                result.getCurrentFeeAmount(),
                result.getOptimalFeeAmount(),
                result.getSavingAmount(),
                result.getSavingPercentage(),
                result.getCreatedAt()
        );
    }
}
