package com.example.api.service;

import com.example.api.dto.request.InterchangeRuleRequest;
import com.example.api.dto.response.InterchangeRuleResponse;
import com.example.api.entity.*;
import com.example.api.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
public class InterchangeRuleService {
    private final InterchangeRuleRepository interchangeRuleRepository;
    private final CardNetworkRepository cardNetworkRepository;
    private final MccCodeRepository mccCodeRepository;
    private final CardTypeRepository cardTypeRepository;
    private final RegionRepository regionRepository;
    private final InterchangeCategoryRepository interchangeCategoryRepository;

    public InterchangeRuleService(InterchangeRuleRepository interchangeRuleRepository, CardNetworkRepository cardNetworkRepository,
                                  MccCodeRepository mccCodeRepository, CardTypeRepository cardTypeRepository,
                                  RegionRepository regionRepository, InterchangeCategoryRepository interchangeCategoryRepository) {
        this.interchangeRuleRepository = interchangeRuleRepository;
        this.cardNetworkRepository = cardNetworkRepository;
        this.mccCodeRepository = mccCodeRepository;
        this.cardTypeRepository = cardTypeRepository;
        this.regionRepository = regionRepository;
        this.interchangeCategoryRepository = interchangeCategoryRepository;
    }

    @Transactional(readOnly = true)
    public List<InterchangeRuleResponse> findAll() {
        return interchangeRuleRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public InterchangeRuleResponse create(InterchangeRuleRequest request) {
        CardNetwork cardNetwork = request.cardNetworkId() == null ? null : cardNetworkRepository.findById(request.cardNetworkId())
                .orElseThrow(() -> new IllegalArgumentException("Card network not found: " + request.cardNetworkId()));
        MccCode mcc = request.mccCode() == null ? null : mccCodeRepository.findById(request.mccCode())
                .orElseThrow(() -> new IllegalArgumentException("MCC not found: " + request.mccCode()));
        CardType cardType = request.cardTypeId() == null ? null : cardTypeRepository.findById(request.cardTypeId())
                .orElseThrow(() -> new IllegalArgumentException("Card type not found: " + request.cardTypeId()));
        Region region = request.regionCode() == null ? null : regionRepository.findById(request.regionCode())
                .orElseThrow(() -> new IllegalArgumentException("Region not found: " + request.regionCode()));
        InterchangeCategory category = interchangeCategoryRepository.findById(request.categoryId())
                .orElseThrow(() -> new IllegalArgumentException("Interchange category not found: " + request.categoryId()));

        InterchangeRule rule = InterchangeRule.builder()
                .rulePriority(request.rulePriority())
                .cardNetwork(cardNetwork)
                .mcc(mcc)
                .cardType(cardType)
                .transactionChannel(request.transactionChannel())
                .region(region)
                .is3dsRequired(request.is3dsRequired())
                .clearingTimeCondition(request.clearingTimeCondition())
                .category(category)
                .feePercentage(request.feePercentage())
                .fixedFeeAmount(request.fixedFeeAmount() == null ? BigDecimal.ZERO : request.fixedFeeAmount())
                .currencyCode(request.currencyCode())
                .build();
        return toResponse(interchangeRuleRepository.save(rule));
    }

    private InterchangeRuleResponse toResponse(InterchangeRule rule) {
        return new InterchangeRuleResponse(
                rule.getRuleId(),
                rule.getRulePriority(),
                rule.getCardNetwork() == null ? null : rule.getCardNetwork().getCardNetworkId(),
                rule.getCardNetwork() == null ? null : rule.getCardNetwork().getNetworkName(),
                rule.getMcc() == null ? null : rule.getMcc().getMccCode(),
                rule.getMcc() == null ? null : rule.getMcc().getMccDescription(),
                rule.getCardType() == null ? null : rule.getCardType().getCardTypeId(),
                rule.getCardType() == null ? null : rule.getCardType().getCardTypeName(),
                rule.getTransactionChannel(),
                rule.getRegion() == null ? null : rule.getRegion().getRegionCode(),
                rule.getRegion() == null ? null : rule.getRegion().getRegionName(),
                rule.getIs3dsRequired(),
                rule.getClearingTimeCondition(),
                rule.getCategory().getCategoryId(),
                rule.getCategory().getCategoryName(),
                rule.getFeePercentage(),
                rule.getFixedFeeAmount(),
                rule.getCurrencyCode()
        );
    }
}
