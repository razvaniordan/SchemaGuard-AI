package com.example.api.service;

import com.example.api.dto.mapper.PythonTransactionMapper;
import com.example.api.dto.request.PythonClassificationRequest;
import com.example.api.dto.request.PythonTransactionInput;
import com.example.api.entity.Transaction;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;

@Service
@RequiredArgsConstructor
public class PythonClassificationService {

    private final RestClient pythonClassificationRestClient;
    private final PythonTransactionMapper mapper;

    public String classify(Transaction transaction) {
        PythonClassificationRequest request = new PythonClassificationRequest(mapper.toPythonInput(transaction));
        try {
        return pythonClassificationRestClient.post()
                .uri("/classify-transaction")
                .body(request)
                .retrieve()
                .body(String.class);
        } catch (HttpClientErrorException e) {
            System.out.println("Python API status: " + e.getStatusCode());
            System.out.println("Python API body: " + e.getResponseBodyAsString());
            System.out.println(request);
            throw e;
        }
    }
}
