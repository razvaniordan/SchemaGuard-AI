package com.example.api.ml.cache;

import com.example.api.entity.AcquiringPartner;
import com.example.api.entity.Bank;
import com.example.api.entity.Card;
import com.example.api.entity.CardNetwork;
import com.example.api.entity.Client;
import com.example.api.entity.MccCode;
import com.example.api.entity.Merchant;
import com.example.api.entity.Region;
import com.example.api.entity.Transaction;
import com.example.api.ml.client.MlCoreClient;
import com.example.api.ml.dto.MlRuleEngineResult;
import com.example.api.ml.mapper.MlRuleEngineResultMapper;
import com.example.api.repository.TransactionRepository;
import com.example.api.ruleengine.model.RuleEngineResult;
import com.example.api.ruleengine.service.RuleEngineService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

@Service
@RequiredArgsConstructor
public class PortfolioAnomalyCacheService {

    private final TransactionRepository transactionRepository;
    private final RuleEngineService ruleEngineService;
    private final MlRuleEngineResultMapper mlRuleEngineResultMapper;
    private final MlCoreClient mlCoreClient;
    private final ObjectMapper objectMapper;

    private final AtomicBoolean refreshInProgress = new AtomicBoolean(false);

    private volatile PortfolioAnomalyCacheStatus cacheStatus = PortfolioAnomalyCacheStatus.EMPTY;
    private volatile Instant refreshedAt;
    private volatile String errorMessage;
    private volatile JsonNode cachedSnapshot;

    public void refresh() {
        if (!refreshInProgress.compareAndSet(false, true)) {
            return;
        }

        cacheStatus = PortfolioAnomalyCacheStatus.REFRESHING;

        try {
            List<Transaction> transactions = transactionRepository.findAll();

            if (transactions.isEmpty()) {
                transactions = List.of(buildDemoTransaction(1L));
            }

            List<MlRuleEngineResult> results = transactions.stream()
                    .map(transaction -> {
                        RuleEngineResult ruleResult = ruleEngineService.evaluate(transaction);
                        return mlRuleEngineResultMapper.toMlResult(transaction, ruleResult);
                    })
                    .toList();

            JsonNode anomaliesRoot = objectMapper.readTree(mlCoreClient.detectAnomalies(results));

            refreshedAt = Instant.now();
            errorMessage = null;
            cacheStatus = PortfolioAnomalyCacheStatus.READY;
            cachedSnapshot = buildSnapshot(anomaliesRoot, PortfolioAnomalyCacheStatus.READY, null);
        } catch (Exception exception) {
            errorMessage = exception.getMessage();
            cacheStatus = PortfolioAnomalyCacheStatus.FAILED;
            cachedSnapshot = buildSnapshot(
                    cachedSnapshot,
                    PortfolioAnomalyCacheStatus.FAILED,
                    errorMessage
            );
        } finally {
            refreshInProgress.set(false);
        }
    }

    public JsonNode getSnapshot() {
        JsonNode snapshot = cachedSnapshot;

        if (snapshot != null) {
            return snapshot;
        }

        return buildSnapshot(
            objectMapper.createObjectNode().putArray("anomalies"),
            PortfolioAnomalyCacheStatus.EMPTY,
            null
        );
    }

    public PortfolioAnomalyCacheStatus getCacheStatus() {
        return cacheStatus;
    }

    public Instant getRefreshedAt() {
        return refreshedAt;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    private ObjectNode buildSnapshot(
            JsonNode anomaliesRoot,
            PortfolioAnomalyCacheStatus status,
            String error
    ) {
        ObjectNode snapshot = objectMapper.createObjectNode();

        if (anomaliesRoot != null && anomaliesRoot.isObject()) {
            snapshot.setAll((ObjectNode) anomaliesRoot);
        } else {
            snapshot.set("anomalies", anomaliesRoot == null ? objectMapper.createArrayNode() : anomaliesRoot);
        }

        snapshot.put("cacheStatus", status.name());

        if (refreshedAt != null) {
            snapshot.put("refreshedAt", refreshedAt.toString());
        } else {
            snapshot.putNull("refreshedAt");
        }

        if (error != null) {
            snapshot.put("errorMessage", error);
        } else {
            snapshot.putNull("errorMessage");
        }

        return snapshot;
    }

    private Transaction buildDemoTransaction(Long transactionId) {
        Transaction tx = new Transaction();

        Client client = new Client();
        client.setClientId(1L);
        client.setClientName("Demo Client");

        Merchant merchant = new Merchant();
        merchant.setMerchantId(1L);
        merchant.setMerchantName("Demo Merchant");

        MccCode demoMccCode = new MccCode();
        demoMccCode.setMccCode("5411");
        demoMccCode.setMccDescription("Grocery Stores, Supermarkets");

        Card card = new Card();
        card.setCardId(1L);

        AcquiringPartner acquiringPartner = new AcquiringPartner();
        acquiringPartner.setAcquiringPartnerId(1L);

        Bank issuerBank = new Bank();
        issuerBank.setBankId(1L);

        CardNetwork cardNetwork = new CardNetwork();
        cardNetwork.setCardNetworkId(1L);

        Region region = new Region();
        region.setRegionCode("EU");

        tx.setTransactionId(transactionId);
        tx.setClient(client);
        tx.setMerchant(merchant);
        tx.setMccCode(demoMccCode);
        tx.setCard(card);
        tx.setAcquiringPartner(acquiringPartner);
        tx.setIssuerBank(issuerBank);
        tx.setCardNetwork(cardNetwork);
        tx.setRegion(region);
        tx.setTransactionAmount(BigDecimal.valueOf(100));
        tx.setTransactionCurrency("RON");
        tx.setTransactionChannel(Transaction.TransactionChannel.ECOMMERCE);
        tx.setAuthorizationDatetime(java.time.LocalDateTime.of(2026, 5, 8, 10, 0));
        tx.setClearingDatetime(java.time.LocalDateTime.of(2026, 5, 10, 10, 0));
        tx.setTransactionStatus(Transaction.TransactionStatus.APPROVED);
        tx.setIs3dsAuthenticated("N");
        tx.setEciValue("07");

        return tx;
    }
}