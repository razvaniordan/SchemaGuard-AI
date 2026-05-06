package com.example.api.service;

import com.example.api.dto.request.CardNetworkRequest;
import com.example.api.dto.response.CardNetworkResponse;
import com.example.api.entity.CardNetwork;
import com.example.api.repository.CardNetworkRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CardNetworkService {
    private final CardNetworkRepository cardNetworkRepository;

    public CardNetworkService(CardNetworkRepository cardNetworkRepository) {
        this.cardNetworkRepository = cardNetworkRepository;
    }

    @Transactional(readOnly = true)
    public List<CardNetworkResponse> findAll() {
        return cardNetworkRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public CardNetworkResponse create(CardNetworkRequest request) {
        CardNetwork cardNetwork = CardNetwork.builder()
                .networkCode(request.networkCode())
                .networkName(request.networkName())
                .build();
        return toResponse(cardNetworkRepository.save(cardNetwork));
    }

    private CardNetworkResponse toResponse(CardNetwork cardNetwork) {
        return new CardNetworkResponse(cardNetwork.getCardNetworkId(), cardNetwork.getNetworkCode(), cardNetwork.getNetworkName());
    }
}
