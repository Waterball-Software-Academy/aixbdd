package ${BASE_PACKAGE}.security;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

/**
 * Utility class for getting current authenticated user information.
 * Equivalent to Python's get_current_user_id dependency in app/core/deps.py
 */
public class CurrentUser {

    /**
     * Get the current user ID from the request.
     *
     * @param request the HTTP request
     * @return the current user ID
     * @throws ResponseStatusException if no authenticated user
     */
    public static Long getId(HttpServletRequest request) {
        Object userId = request.getAttribute(JwtTokenFilter.CURRENT_USER_ID_ATTRIBUTE);
        if (userId == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "無效的認證憑證");
        }
        return (Long) userId;
    }

    /**
     * Get the current user ID from the request, or null if not authenticated.
     *
     * @param request the HTTP request
     * @return the current user ID or null
     */
    public static Long getIdOrNull(HttpServletRequest request) {
        Object userId = request.getAttribute(JwtTokenFilter.CURRENT_USER_ID_ATTRIBUTE);
        return userId != null ? (Long) userId : null;
    }
}
