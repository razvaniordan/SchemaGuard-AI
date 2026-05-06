package com.example.api.service;

import com.example.api.dto.request.BankRequest;
import com.example.api.dto.response.BankResponse;
import com.example.api.entity.Bank;
import com.example.api.entity.Country;
import com.example.api.repository.BankRepository;
import com.example.api.repository.CountryRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class BankService {
    private final BankRepository bankRepository;
    private final CountryRepository countryRepository;

    public BankService(BankRepository bankRepository, CountryRepository countryRepository) {
        this.bankRepository = bankRepository;
        this.countryRepository = countryRepository;
    }

    @Transactional(readOnly = true)
    public List<BankResponse> findAll() {
        return bankRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public BankResponse create(BankRequest request) {
        Country country = countryRepository.findById(request.countryCode())
                .orElseThrow(() -> new IllegalArgumentException("Country not found: " + request.countryCode()));
        Bank bank = Bank.builder().bankName(request.bankName()).country(country).build();
        return toResponse(bankRepository.save(bank));
    }

    private BankResponse toResponse(Bank bank) {
        return new BankResponse(bank.getBankId(), bank.getBankName(), bank.getCountry().getCountryCode(), bank.getCountry().getCountryName());
    }
}
