package com.example.api.ml.client;

import com.example.api.ml.dto.MlFeeComparisonRequest;
import com.example.api.ml.dto.MlMissedConditionRequest;
import com.example.api.ml.dto.MlRecommendationRequest;
import com.example.api.ml.dto.MlRuleEngineResult;
import com.example.api.ml.dto.MlSimulationRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

import java.util.List;

@RequiredArgsConstructor
@Component
public class MlCoreClient {

    private final RestClient mlCoreRestClient;
    private final ObjectMapper objectMapper;

    public String compareFees(MlFeeComparisonRequest request) {
        return postJson("/ml-core/compare-fees", request, "compare-fees");
    }

    public String prioritizeRecommendations(MlRecommendationRequest request) {
        return postJson(
                "/ml-core/prioritize-recommendations",
                request,
                "prioritize-recommendations"
        );
    }

    public String simulateTransaction(MlSimulationRequest request) {
        return postJson(
                "/simulate-transaction",
                request,
                "simulate-transaction"
        );
    }

    public String missedConditions(MlMissedConditionRequest request) {
        return postJson(
                "/missed-conditions",
                request,
                "missed-conditions"
        );
    }

    public String detectAnomalies(List<MlRuleEngineResult> ruleEngineResults) {
        return postJson(
                "/ml-core/detect-anomalies",
                ruleEngineResults,
                "detect-anomalies"
        );
    }

    private String postJson(String uri, Object request, String endpointName) {
        try {
            String jsonBody = objectMapper.writeValueAsString(request);

            System.out.println("Calling Python ML endpoint: " + endpointName);
            System.out.println("Sending ML JSON:");
            System.out.println(jsonBody);

            return mlCoreRestClient.post()
                    .uri(uri)
                    .contentType(MediaType.APPLICATION_JSON)
                    .accept(MediaType.APPLICATION_JSON)
                    .body(jsonBody)
                    .retrieve()
                    .body(String.class);

        } catch (HttpClientErrorException e) {
            logPythonError(endpointName, e);
            throw e;

        } catch (ResourceAccessException e) {
            logConnectionError(endpointName, e);
            throw e;

        } catch (Exception e) {
            System.out.println("ML Core endpoint failed: " + endpointName);
            e.printStackTrace();
            throw new RuntimeException("ML Core call failed: " + endpointName, e);
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