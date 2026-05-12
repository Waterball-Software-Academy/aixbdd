package ${BASE_PACKAGE}.cucumber;

import io.cucumber.spring.ScenarioScope;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

/**
 * 場景生命週期內的鍵值儲存容器。
 * <p>
 * 每個 Cucumber Scenario 執行期間持有一個 ScenarioContext 實例；
 * {@code DatabaseCleanupHook.@Before(order=0)} 在每個 scenario 開始前呼叫 {@code clear()} 重置。
 */
@Component
@ScenarioScope
public class ScenarioContext {

    private ResponseEntity<?> lastResponse;
    /** 自然鍵 → DB id，例如 {"小明": 1L}，供 ScenarioContextHelper.getUserId() 使用。 */
    private final Map<String, Object> ids = new HashMap<>();
    /** scenario 暫存的任意鍵值對。 */
    private final Map<String, Object> memo = new HashMap<>();
    private String jwtToken;
    private Object queryResult;
    private String lastError;

    // ── lastResponse ──────────────────────────────────────────────────────────

    public ResponseEntity<?> getLastResponse() {
        return lastResponse;
    }

    public void setLastResponse(ResponseEntity<?> lastResponse) {
        this.lastResponse = lastResponse;
    }

    // ── ids（自然鍵 → DB id）──────────────────────────────────────────────────

    public void putId(String name, Object id) {
        ids.put(name, id);
    }

    public Object getId(String name) {
        return ids.get(name);
    }

    public boolean hasId(String name) {
        return ids.containsKey(name);
    }

    // ── memo（scenario 暫存）──────────────────────────────────────────────────

    public void putMemo(String key, Object value) {
        memo.put(key, value);
    }

    public Object getMemo(String key) {
        return memo.get(key);
    }

    // ── jwtToken ──────────────────────────────────────────────────────────────

    public String getJwtToken() {
        return jwtToken;
    }

    public void setJwtToken(String jwtToken) {
        this.jwtToken = jwtToken;
    }

    // ── queryResult ───────────────────────────────────────────────────────────

    public Object getQueryResult() {
        return queryResult;
    }

    public void setQueryResult(Object queryResult) {
        this.queryResult = queryResult;
    }

    // ── lastError ─────────────────────────────────────────────────────────────

    public String getLastError() {
        return lastError;
    }

    public void setLastError(String lastError) {
        this.lastError = lastError;
    }

    // ── lifecycle ─────────────────────────────────────────────────────────────

    /** 由 DatabaseCleanupHook.@Before(order=0) 呼叫，重置所有欄位。 */
    public void clear() {
        this.lastResponse = null;
        this.ids.clear();
        this.memo.clear();
        this.jwtToken = null;
        this.queryResult = null;
        this.lastError = null;
    }
}