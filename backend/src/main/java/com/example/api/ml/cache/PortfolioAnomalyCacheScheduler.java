package com.example.api.ml.cache;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class PortfolioAnomalyCacheScheduler {

    private final PortfolioAnomalyCacheService portfolioAnomalyCacheService;

    @PostConstruct
    public void refreshOnStartup() {
        portfolioAnomalyCacheService.refresh();
    }

    @Scheduled(fixedRate = 300000)
    public void refreshEveryFiveMinutes() {
        portfolioAnomalyCacheService.refresh();
    }
}