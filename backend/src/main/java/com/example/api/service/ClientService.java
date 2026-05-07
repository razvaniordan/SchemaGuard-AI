package com.example.api.service;

import com.example.api.dto.request.ClientRequest;
import com.example.api.dto.response.ClientResponse;
import com.example.api.entity.Client;
import com.example.api.entity.Country;
import com.example.api.repository.ClientRepository;
import com.example.api.repository.CountryRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class ClientService {

    private final ClientRepository clientRepository;
    private final CountryRepository countryRepository;

    public ClientService(ClientRepository clientRepository,
                         CountryRepository countryRepository) {
        this.clientRepository = clientRepository;
        this.countryRepository = countryRepository;
    }

    @Transactional(readOnly = true)
    public List<ClientResponse> findAll() {
        return clientRepository.findAll()
                .stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional
    public ClientResponse create(ClientRequest request) {
        Country country = countryRepository.findById(request.countryCode())
                .orElseThrow(() -> new IllegalArgumentException(
                        "Country not found: " + request.countryCode()
                ));

        Client client = Client.builder()
                .clientName(request.clientName())
                .country(country)
                .build();

        Client saved = clientRepository.save(client);

        return toResponse(saved);
    }

    private ClientResponse toResponse(Client client) {
        return new ClientResponse(
                client.getClientId(),
                client.getClientName(),
                client.getCountry().getCountryCode(),
                client.getCountry().getCountryName()
        );
    }
}