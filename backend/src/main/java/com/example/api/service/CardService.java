package com.example.api.service;

import com.example.api.dto.request.CardRequest;
import com.example.api.dto.response.CardResponse;
import com.example.api.entity.*;
import com.example.api.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CardService {
    private final CardRepository cardRepository;
    private final ClientRepository clientRepository;
    private final BankRepository bankRepository;
    private final CardNetworkRepository cardNetworkRepository;
    private final CardTypeRepository cardTypeRepository;

    public CardService(CardRepository cardRepository, ClientRepository clientRepository, BankRepository bankRepository,
                       CardNetworkRepository cardNetworkRepository, CardTypeRepository cardTypeRepository) {
        this.cardRepository = cardRepository;
        this.clientRepository = clientRepository;
        this.bankRepository = bankRepository;
        this.cardNetworkRepository = cardNetworkRepository;
        this.cardTypeRepository = cardTypeRepository;
    }

    @Transactional(readOnly = true)
    public List<CardResponse> findAll() {
        return cardRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public CardResponse create(CardRequest request) {
        Client client = clientRepository.findById(request.clientId())
                .orElseThrow(() -> new IllegalArgumentException("Client not found: " + request.clientId()));
        Bank issuerBank = bankRepository.findById(request.issuerBankId())
                .orElseThrow(() -> new IllegalArgumentException("Issuer bank not found: " + request.issuerBankId()));
        CardNetwork cardNetwork = cardNetworkRepository.findById(request.cardNetworkId())
                .orElseThrow(() -> new IllegalArgumentException("Card network not found: " + request.cardNetworkId()));
        CardType cardType = cardTypeRepository.findById(request.cardTypeId())
                .orElseThrow(() -> new IllegalArgumentException("Card type not found: " + request.cardTypeId()));

        Card card = Card.builder()
                .client(client)
                .issuerBank(issuerBank)
                .cardNetwork(cardNetwork)
                .cardType(cardType)
                .cardProductType(request.cardProductType())
                .build();
        return toResponse(cardRepository.save(card));
    }

    private CardResponse toResponse(Card card) {
        return new CardResponse(
                card.getCardId(),
                card.getClient().getClientId(),
                card.getClient().getClientName(),
                card.getIssuerBank().getBankId(),
                card.getIssuerBank().getBankName(),
                card.getCardNetwork().getCardNetworkId(),
                card.getCardNetwork().getNetworkName(),
                card.getCardType().getCardTypeId(),
                card.getCardType().getCardTypeName(),
                card.getCardProductType()
        );
    }
}
