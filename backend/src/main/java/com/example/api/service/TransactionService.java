package com.example.api.service;

import com.example.api.dto.request.TransactionRequest;
import com.example.api.dto.response.TransactionResponse;
import com.example.api.entity.*;
import com.example.api.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class TransactionService {

    private final TransactionRepository transactionRepository;
    private final ClientRepository clientRepository;
    private final MerchantRepository merchantRepository;
    private final CardRepository cardRepository;
    private final AcquiringPartnerRepository acquiringPartnerRepository;
    private final BankRepository bankRepository;
    private final CardNetworkRepository cardNetworkRepository;
    private final RegionRepository regionRepository;

    public TransactionService(
            TransactionRepository transactionRepository,
            ClientRepository clientRepository,
            MerchantRepository merchantRepository,
            CardRepository cardRepository,
            AcquiringPartnerRepository acquiringPartnerRepository,
            BankRepository bankRepository,
            CardNetworkRepository cardNetworkRepository,
            RegionRepository regionRepository
    ) {
        this.transactionRepository = transactionRepository;
        this.clientRepository = clientRepository;
        this.merchantRepository = merchantRepository;
        this.cardRepository = cardRepository;
        this.acquiringPartnerRepository = acquiringPartnerRepository;
        this.bankRepository = bankRepository;
        this.cardNetworkRepository = cardNetworkRepository;
        this.regionRepository = regionRepository;
    }

    @Transactional(readOnly = true)
    public List<TransactionResponse> findAll() {
        return transactionRepository.findAll()
                .stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional
    public TransactionResponse create(TransactionRequest request) {
        Client client = clientRepository.findById(request.clientId())
                .orElseThrow(() -> new IllegalArgumentException("Client not found: " + request.clientId()));

        Merchant merchant = merchantRepository.findById(request.merchantId())
                .orElseThrow(() -> new IllegalArgumentException("Merchant not found: " + request.merchantId()));

        Card card = cardRepository.findById(request.cardId())
                .orElseThrow(() -> new IllegalArgumentException("Card not found: " + request.cardId()));

        AcquiringPartner acquiringPartner = acquiringPartnerRepository.findById(request.acquiringPartnerId())
                .orElseThrow(() -> new IllegalArgumentException("Acquiring partner not found: " + request.acquiringPartnerId()));

        Bank issuerBank = bankRepository.findById(request.issuerBankId())
                .orElseThrow(() -> new IllegalArgumentException("Issuer bank not found: " + request.issuerBankId()));

        CardNetwork cardNetwork = cardNetworkRepository.findById(request.cardNetworkId())
                .orElseThrow(() -> new IllegalArgumentException("Card network not found: " + request.cardNetworkId()));

        Region region = regionRepository.findById(request.regionCode())
                .orElseThrow(() -> new IllegalArgumentException("Region not found: " + request.regionCode()));

        Transaction transaction = Transaction.builder()
                .client(client)
                .merchant(merchant)
                .card(card)
                .acquiringPartner(acquiringPartner)
                .issuerBank(issuerBank)
                .cardNetwork(cardNetwork)
                .region(region)
                .transactionAmount(request.transactionAmount())
                .transactionCurrency(request.transactionCurrency())
                .transactionChannel(request.transactionChannel())
                .authorizationDatetime(request.authorizationDatetime())
                .clearingDatetime(request.clearingDatetime())
                .transactionStatus(request.transactionStatus())
                .is3dsAuthenticated(
                        request.is3dsAuthenticated() == null ? "N" : request.is3dsAuthenticated()
                )
                .eciValue(request.eciValue())
                .build();

        Transaction saved = transactionRepository.save(transaction);

        return toResponse(saved);
    }

    private TransactionResponse toResponse(Transaction transaction) {
        return new TransactionResponse(
                transaction.getTransactionId(),

                transaction.getClient().getClientId(),
                transaction.getClient().getClientName(),

                transaction.getMerchant().getMerchantId(),
                transaction.getMerchant().getMerchantName(),
                transaction.getMccCode().getMccCode(),

                transaction.getCard().getCardId(),
                transaction.getAcquiringPartner().getAcquiringPartnerId(),
                transaction.getIssuerBank().getBankId(),
                transaction.getCardNetwork().getCardNetworkId(),

                transaction.getTransactionAmount(),
                transaction.getTransactionCurrency(),
                transaction.getTransactionChannel(),

                transaction.getAuthorizationDatetime(),
                transaction.getClearingDatetime(),

                transaction.getTransactionStatus(),
                transaction.getIs3dsAuthenticated(),
                transaction.getEciValue(),

                transaction.getRegion().getRegionCode()
        );
    }
}