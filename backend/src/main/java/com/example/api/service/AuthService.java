package com.example.api.service;

import com.example.api.dto.LoginRequest;
import com.example.api.dto.LoginResponse;
import com.example.api.security.TokenService;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.stereotype.Service;

@Service
public class AuthService {
    private final TokenService tokenService;

    public AuthService(TokenService tokenService) {
        this.tokenService = tokenService;
    }

    public LoginResponse login(LoginRequest request) {
        // Demo-only credentials. Replace with database-backed authentication later.
        if (!"demo".equals(request.username()) || !"password".equals(request.password())) {
            throw new BadCredentialsException("Invalid username or password");
        }
        return new LoginResponse(tokenService.generateToken(request.username()), "Bearer");
    }
}
