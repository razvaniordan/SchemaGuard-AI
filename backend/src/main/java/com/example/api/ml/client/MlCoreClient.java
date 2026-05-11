package com.example.api.ml.client;

import com.example.api.ml.dto.MlFeeComparisonRequest;
import com.example.api.ml.dto.MlMissedConditionRequest;
import com.example.api.ml.dto.MlRecommendationRequest;
import com.example.api.ml.dto.MlRuleEngineResult;
import com.example.api.ml.dto.MlSimulationRequest;
import org.springframework.stereotype.Component;
import org.springframework.http.MediaType;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.MediaType;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

import java.util.List;

@Component
public class MlCoreClient {

    // Local Python ML Core service.
    // For local development, ML Core runs on http://localhost:8001.
    private final RestClient mlCoreRestClient = RestClient.builder()
            .baseUrl("http://localhost:8001")
            .build();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public String compareFees(MlFeeComparisonRequest request) {
        try {
            String jsonBody = objectMapper.writeValueAsString(request);

            System.out.println("Sending ML compare-fees JSON:");
            System.out.println(jsonBody);

            return mlCoreRestClient.post()
                    .uri("/ml-core/compare-fees")
                    .contentType(MediaType.APPLICATION_JSON)
                    .accept(MediaType.APPLICATION_JSON)
                    .body(jsonBody)
                    .retrieve()
                    .body(String.class);

        } catch (HttpClientErrorException e) {
            logPythonError("compare-fees", e);
            throw e;
        } catch (Exception e) {
            System.out.println("compare-fees call failed");
            e.printStackTrace();
            throw new RuntimeException(e);
        }
    }
    public String prioritizeRecommendations(MlRecommendationRequest request) {
        try {
            return mlCoreRestClient.post()
                    .uri("/ml-core/prioritize-recommendations")
                    .body(request)
                    .retrieve()
                    .body(String.class);
        } catch (HttpClientErrorException e) {
            logPythonError("prioritize-recommendations", e);
            throw e;
        } catch (ResourceAccessException e) {
            logConnectionError("prioritize-recommendations", e);
            throw e;
        }
    }

    public String simulateTransaction(MlSimulationRequest request) {
        try {
            return mlCoreRestClient.post()
                    .uri("/simulate-transaction")
                    .body(request)
                    .retrieve()
                    .body(String.class);
        } catch (HttpClientErrorException e) {
            logPythonError("simulate-transaction", e);
            throw e;
        } catch (ResourceAccessException e) {
            logConnectionError("simulate-transaction", e);
            throw e;
        }
    }

    public String missedConditions(MlMissedConditionRequest request) {
        try {
            return mlCoreRestClient.post()
                    .uri("/ml-core/missed-conditions")
                    .body(request)
                    .retrieve()
                    .body(String.class);
        } catch (HttpClientErrorException e) {
            logPythonError("missed-conditions", e);
            throw e;
        } catch (ResourceAccessException e) {
            logConnectionError("missed-conditions", e);
            throw e;
        }
    }

    public String detectAnomalies(List<MlRuleEngineResult> ruleEngineResults) {
        try {
            return mlCoreRestClient.post()
                    .uri("/ml-core/detect-anomalies")
                    .body(ruleEngineResults)
                    .retrieve()
                    .body(String.class);
        } catch (HttpClientErrorException e) {
            logPythonError("detect-anomalies", e);
            throw e;
        } catch (ResourceAccessException e) {
            logConnectionError("detect-anomalies", e);
            throw e;
        }
    }

    private void logPythonError(String endpointName, HttpClientErrorException e) {
        System.out.println("ML Core endpoint failed: " + endpointName);
        System.out.println("Python API status: " + e.getStatusCode());
        System.out.println("Python API body: " + e.getResponseBodyAsString());
    }

    private void logConnectionError(String endpointName, ResourceAccessException e) {
        System.out.println("Could not connect to ML Core endpoint: " + endpointName);
        System.out.println("Expected ML Core URL: http://localhost:8001");
        System.out.println("Connection error: " + e.getMessage());
    }
}