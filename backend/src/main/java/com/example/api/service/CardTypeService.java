package com.example.api.service;

import com.example.api.dto.request.CardTypeRequest;
import com.example.api.dto.response.CardTypeResponse;
import com.example.api.entity.CardType;
import com.example.api.repository.CardTypeRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CardTypeService {
    private final CardTypeRepository cardTypeRepository;

    public CardTypeService(CardTypeRepository cardTypeRepository) {
        this.cardTypeRepository = cardTypeRepository;
    }

    @Transactional(readOnly = true)
    public List<CardTypeResponse> findAll() {
        return cardTypeRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public CardTypeResponse create(CardTypeRequest request) {
        CardType cardType = CardType.builder()
                .cardTypeName(request.cardTypeName())
                .description(request.description())
                .build();
        return toResponse(cardTypeRepository.save(cardType));
    }

    private CardTypeResponse toResponse(CardType cardType) {
        return new CardTypeResponse(cardType.getCardTypeId(), cardType.getCardTypeName(), cardType.getDescription());
    }
}
