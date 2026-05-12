package com.example.backend.cucumber;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;

/**
 * JWT Helper for generating tokens in tests
 * Equivalent to Python's JwtHelper in tests/features/helpers/
 */
@Component
public class JwtHelper {

    private final SecretKey secretKey;
    private final int expireHours;

    public JwtHelper(
            @Value("${jwt.secret-key:test-secret-key-do-not-use-in-production}") String secretKeyString,
            @Value("${jwt.expire-hours:1}") int expireHours) {
        this.secretKey = Keys.hmacShaKeyFor(secretKeyString.getBytes(StandardCharsets.UTF_8));
        this.expireHours = expireHours;
    }

    /**
     * Generate a JWT token for the given user ID
     *
     * @param userId the user ID to include in the token
     * @return the JWT token string
     */
    public String generateToken(String userId) {
        Instant now = Instant.now();
        Instant expiry = now.plus(expireHours, ChronoUnit.HOURS);

        return Jwts.builder()
                .subject(userId)
                .issuedAt(Date.from(now))
                .expiration(Date.from(expiry))
                .signWith(secretKey)
                .compact();
    }

    /**
     * Verify and decode a JWT token
     *
     * @param token the JWT token to verify
     * @return the user ID from the token
     */
    public String verifyToken(String token) {
        return Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload()
                .getSubject();
    }
}
