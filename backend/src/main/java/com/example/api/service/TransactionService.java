package com.example.api.service;

import com.example.api.dto.TransactionRequest;
import com.example.api.dto.TransactionResponse;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
public class TransactionService {
    private final List<TransactionResponse> transactions = new CopyOnWriteArrayList<>();

    public List<TransactionResponse> findAll() {
        return transactions;
    }

    public TransactionResponse create(TransactionRequest request) {
        var response = new TransactionResponse(
                UUID.randomUUID().toString(),
                request.merchantName(),
                request.mcc(),
                request.amount(),
                request.currency(),
                Instant.now()
        );
        transactions.add(response);
        return response;
    }
}
