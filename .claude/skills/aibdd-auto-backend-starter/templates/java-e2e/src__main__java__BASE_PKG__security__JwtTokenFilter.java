package ${BASE_PACKAGE}.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.crypto.SecretKey;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

/**
 * JWT Token Filter for validating JWT tokens on incoming requests.
 * Equivalent to Python's get_current_user_id in app/core/deps.py
 *
 * Stores the authenticated user ID in request attribute "currentUserId"
 * for downstream controllers to access.
 */
@Component
public class JwtTokenFilter extends OncePerRequestFilter {

    public static final String CURRENT_USER_ID_ATTRIBUTE = "currentUserId";

    private final SecretKey secretKey;

    public JwtTokenFilter(
            @Value("${jwt.secret-key:chapter04-test-secret-key-do-not-use-in-production}") String secretKeyString) {
        this.secretKey = Keys.hmacShaKeyFor(secretKeyString.getBytes(StandardCharsets.UTF_8));
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);

            try {
                Claims claims = Jwts.parser()
                        .verifyWith(secretKey)
                        .build()
                        .parseSignedClaims(token)
                        .getPayload();

                String userId = claims.getSubject();

                if (userId != null) {
                    // Store user ID in request attribute for controllers to access
                    request.setAttribute(CURRENT_USER_ID_ATTRIBUTE, Long.parseLong(userId));
                }
            } catch (ExpiredJwtException e) {
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.setContentType("application/json;charset=UTF-8");
                response.getWriter().write("{\"detail\":\"Token 已過期\"}");
                return;
            } catch (Exception e) {
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.setContentType("application/json;charset=UTF-8");
                response.getWriter().write("{\"detail\":\"無效的 Token\"}");
                return;
            }
        }

        filterChain.doFilter(request, response);
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
