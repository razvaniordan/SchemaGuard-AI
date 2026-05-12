package com.example.api.ml.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class MlCoreConfig {

    @Bean
    public RestClient mlCoreRestClient(RestClient.Builder builder) {

        return builder
                .baseUrl("http://host.docker.internal:8001")
                .build();
    }
}