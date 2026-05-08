package com.example.api.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class PythonClassificationClientConfig {



    @Bean
    public RestClient pythonClassificationRestClient(
            //@Value("http://rule-engine-python:8090") String baseUrl
    ) {
        return RestClient.builder()
                .baseUrl("http://rule-engine-python:8090")
                .build();
    }
}