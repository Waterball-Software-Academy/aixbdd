# 答案解析閘門

## Rule 1 — 模糊／重複／缺題就標 unresolved 並 STOP，禁止靜默猜值

- 收完一批答案後，每題都必須有「唯一、明確、可消費」的 resolved value 才算通過。只要某題沒回答、回答看不出對應哪個 option、同題被回了互斥兩值、或一個 reply token 同時像在回兩題，這題就是 `unresolved`：在 `${PLAN_PATH}` 標記、告知 user、STOP 整個 skill。kickoff 每個答案都會固化成下游 artifact（boundary id、stack tail、語系），猜錯一個值會無聲灌進 skeleton、到 build／測試才爆，根因早被埋。寧可停在這裡讓人補一句，也不要讓錯誤決策往下游擴散。

### ✅ Good

情境：Q3 回 `course api`（含空白，非合法 kebab-case）

```
→ ${PLAN_PATH} q3.status = unresolved
→ 告知 user：「q3-backend-service-name 已標記 unresolved（含空白，需 kebab-case），請重答」
→ STOP
```

### ❌ Bad

```
同一批回答：Q1: python_e2e、Q1: java_e2e（同題互斥兩值）
AI：「兩個都有提到，我先採用 python_e2e 繼續。」
（靜默選一個 → 下游 skeleton 可能整套錯 stack）
```

**預期改法**
- 偵測到 q1 同題兩個互斥值 → 標 unresolved、回報「q1 收到互斥答案 python_e2e／java_e2e，請擇一重答」、STOP。
