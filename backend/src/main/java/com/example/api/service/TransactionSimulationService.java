package com.example.api.service;

import com.example.api.dto.request.TransactionSimulationRequest;
import com.example.api.dto.response.TransactionSimulationResponse;
import com.example.api.entity.Region;
import com.example.api.entity.Transaction;
import com.example.api.entity.TransactionSimulation;
import com.example.api.repository.RegionRepository;
import com.example.api.repository.TransactionRepository;
import com.example.api.repository.TransactionSimulationRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class TransactionSimulationService {
    private final TransactionSimulationRepository simulationRepository;
    private final TransactionRepository transactionRepository;
    private final RegionRepository regionRepository;

    public TransactionSimulationService(TransactionSimulationRepository simulationRepository,
                                        TransactionRepository transactionRepository,
                                        RegionRepository regionRepository) {
        this.simulationRepository = simulationRepository;
        this.transactionRepository = transactionRepository;
        this.regionRepository = regionRepository;
    }

    @Transactional(readOnly = true)
    public List<TransactionSimulationResponse> findAll() {
        return simulationRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public TransactionSimulationResponse create(TransactionSimulationRequest request) {
        Transaction transaction = transactionRepository.findById(request.transactionId())
                .orElseThrow(() -> new IllegalArgumentException("Transaction not found: " + request.transactionId()));
        Region region = request.simulatedRegionCode() == null ? null : regionRepository.findById(request.simulatedRegionCode())
                .orElseThrow(() -> new IllegalArgumentException("Region not found: " + request.simulatedRegionCode()));

        TransactionSimulation simulation = TransactionSimulation.builder()
                .transaction(transaction)
                .simulatedIs3dsAuthenticated(request.simulatedIs3dsAuthenticated())
                .simulatedEciValue(request.simulatedEciValue())
                .simulatedClearingDatetime(request.simulatedClearingDatetime())
                .simulatedRegion(region)
                .simulationReason(request.simulationReason())
                .build();
        return toResponse(simulationRepository.save(simulation));
    }

    private TransactionSimulationResponse toResponse(TransactionSimulation simulation) {
        return new TransactionSimulationResponse(
                simulation.getSimulationId(),
                simulation.getTransaction().getTransactionId(),
                simulation.getSimulatedIs3dsAuthenticated(),
                simulation.getSimulatedEciValue(),
                simulation.getSimulatedClearingDatetime(),
                simulation.getSimulatedRegion() == null ? null : simulation.getSimulatedRegion().getRegionCode(),
                simulation.getSimulatedRegion() == null ? null : simulation.getSimulatedRegion().getRegionName(),
                simulation.getSimulationReason(),
                simulation.getCreatedAt()
        );
    }
}
