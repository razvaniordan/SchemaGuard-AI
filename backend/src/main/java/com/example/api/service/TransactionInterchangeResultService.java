package com.example.api.service;

import com.example.api.dto.request.TransactionInterchangeResultRequest;
import com.example.api.dto.response.TransactionInterchangeResultResponse;
import com.example.api.entity.*;
import com.example.api.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
public class TransactionInterchangeResultService {
    private final TransactionInterchangeResultRepository resultRepository;
    private final TransactionRepository transactionRepository;
    private final InterchangeCategoryRepository categoryRepository;
    private final InterchangeRuleRepository ruleRepository;

    public TransactionInterchangeResultService(TransactionInterchangeResultRepository resultRepository, TransactionRepository transactionRepository,
                                               InterchangeCategoryRepository categoryRepository, InterchangeRuleRepository ruleRepository) {
        this.resultRepository = resultRepository;
        this.transactionRepository = transactionRepository;
        this.categoryRepository = categoryRepository;
        this.ruleRepository = ruleRepository;
    }

    @Transactional(readOnly = true)
    public List<TransactionInterchangeResultResponse> findAll() {
        return resultRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public TransactionInterchangeResultResponse create(TransactionInterchangeResultRequest request) {
        Transaction transaction = transactionRepository.findById(request.transactionId())
                .orElseThrow(() -> new IllegalArgumentException("Transaction not found: " + request.transactionId()));
        InterchangeCategory category = categoryRepository.findById(request.categoryId())
                .orElseThrow(() -> new IllegalArgumentException("Interchange category not found: " + request.categoryId()));
        InterchangeRule appliedRule = request.appliedRuleId() == null ? null : ruleRepository.findById(request.appliedRuleId())
                .orElseThrow(() -> new IllegalArgumentException("Interchange rule not found: " + request.appliedRuleId()));

        TransactionInterchangeResult result = TransactionInterchangeResult.builder()
                .transaction(transaction)
                .resultType(request.resultType())
                .category(category)
                .appliedRule(appliedRule)
                .feePercentage(request.feePercentage())
                .fixedFeeAmount(request.fixedFeeAmount() == null ? BigDecimal.ZERO : request.fixedFeeAmount())
                .interchangeFeeAmount(request.interchangeFeeAmount())
                .build();
        return toResponse(resultRepository.save(result));
    }

    private TransactionInterchangeResultResponse toResponse(TransactionInterchangeResult result) {
        return new TransactionInterchangeResultResponse(
                result.getResultId(),
                result.getTransaction().getTransactionId(),
                result.getResultType(),
                result.getCategory().getCategoryId(),
                result.getCategory().getCategoryName(),
                result.getAppliedRule() == null ? null : result.getAppliedRule().getRuleId(),
                result.getFeePercentage(),
                result.getFixedFeeAmount(),
                result.getInterchangeFeeAmount(),
                result.getEvaluatedAt()
        );
    }
}
