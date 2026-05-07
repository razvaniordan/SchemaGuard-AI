package com.example.api.controller;

import com.example.api.entity.Transaction;
import com.example.api.repository.TransactionRepository;
import com.example.api.service.PythonClassificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/transactions")
@RequiredArgsConstructor
public class TransactionClassificationController {

    private final TransactionRepository transactionRepository;
    private final PythonClassificationService pythonClassificationService;

    @PostMapping("/{transactionId}/classify")
    @Transactional(readOnly = true)
    public String classify(@PathVariable Long transactionId) {
        Transaction transaction = transactionRepository.findById(transactionId)
                .orElseThrow(() -> new RuntimeException("Transaction not found: " + transactionId));

        return pythonClassificationService.classify(transaction);
    }
}