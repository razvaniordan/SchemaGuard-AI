package com.example.api.ml.client;

import com.example.api.ml.dto.MlFeeComparisonRequest;
import com.example.api.ml.dto.MlMissedConditionRequest;
import com.example.api.ml.dto.MlRecommendationRequest;
import com.example.api.ml.dto.MlRuleEngineResult;
import com.example.api.ml.dto.MlSimulationRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;

import java.util.List;

@Component
@RequiredArgsConstructor
public class MlCoreClient {

    // RestClient configured with the base URL of the Python ML Core service.
    // Example base URL: http://localhost:8001
    private final RestClient mlCoreRestClient;

    /**
     * Calls ML Core fee comparison endpoint.
     *
     * Used for:
     * - current fee vs optimized fee comparison
     * - ML-predicted savings
     * - monthly/yearly projections
     */
    public String compareFees(MlFeeComparisonRequest request) {
        try {
            return mlCoreRestClient.post()
                    .uri("/ml-core/compare-fees")
                    .body(request)
                    .retrieve()
                    .body(String.class);
        } catch (HttpClientErrorException e) {
            logPythonError("compare-fees", e);
            throw e;
        }
    }

    /**
     * Calls ML Core recommendation prioritization endpoint.
     *
     * Used for:
     * - AI-ranked optimization suggestions
     * - recommendation confidence
     * - ranking reason
     */
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
        }
    }

    /**
     * Calls ML Core transaction simulation endpoint.
     *
     * Used for:
     * - applying suggested transaction changes
     * - generating simulated transaction payload
     * - validating optimized transaction format
     */
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
        }
    }

    /**
     * Calls ML Core missed condition analysis endpoint.
     *
     * Used for:
     * - explainability
     * - root-cause style missed condition summaries
     * - current vs optimal transaction comparison
     */
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
        }
    }

    /**
     * Calls ML Core anomaly detection endpoint.
     *
     * The Python endpoint expects a raw JSON array at the request body root,
     * not an object wrapper like { "results": [...] }.
     */
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
        }
    }

    /**
     * Logs Python-side validation/API errors clearly.
     *
     * This helps debug schema mismatches between Java DTOs
     * and the FastAPI/Pydantic models in ml-python.
     */
    private void logPythonError(String endpointName, HttpClientErrorException e) {
        System.out.println("ML Core endpoint failed: " + endpointName);
        System.out.println("Python API status: " + e.getStatusCode());
        System.out.println("Python API body: " + e.getResponseBodyAsString());
    }
}