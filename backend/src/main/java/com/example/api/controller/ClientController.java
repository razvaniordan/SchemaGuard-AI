package com.example.api.controller;

import com.example.api.dto.request.ClientRequest;
import com.example.api.dto.response.ClientResponse;
import com.example.api.service.ClientService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/clients")
@Tag(name = "Clients")
@SecurityRequirement(name = "bearerAuth")
public class ClientController {

    private final ClientService clientService;

    public ClientController(ClientService clientService) {
        this.clientService = clientService;
    }

    @GetMapping
    @Operation(summary = "List clients")
    public List<ClientResponse> findAll() {
        return clientService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a client")
    public ClientResponse create(@Valid @RequestBody ClientRequest request) {
        return clientService.create(request);
    }
}