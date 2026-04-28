package com.example.api.security;

import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Base64;

@Service
public class TokenService {
    private static final String DEMO_TOKEN_PREFIX = "demo-jwt";

    public String generateToken(String username) {
        String payload = username + ":" + Instant.now().getEpochSecond();
        return DEMO_TOKEN_PREFIX + "." + Base64.getUrlEncoder().withoutPadding()
                .encodeToString(payload.getBytes(StandardCharsets.UTF_8));
    }

    public boolean isValid(String token) {
        return token != null && token.startsWith(DEMO_TOKEN_PREFIX + ".");
    }

    public String usernameFromToken(String token) {
        if (!isValid(token)) {
            return null;
        }
        try {
            String encodedPayload = token.substring((DEMO_TOKEN_PREFIX + ".").length());
            String decoded = new String(Base64.getUrlDecoder().decode(encodedPayload), StandardCharsets.UTF_8);
            return decoded.split(":", 2)[0];
        } catch (IllegalArgumentException ex) {
            return null;
        }
    }
}
