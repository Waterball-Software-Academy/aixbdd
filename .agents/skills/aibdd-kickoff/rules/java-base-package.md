# Java base_package 推導

## Rule 1 — base_package 從 tlb_id 推導時必須 strip 掉 hyphen，產出合法 Java package

- `java_e2e` 要把 `${KICKOFF_BASE_PACKAGE}` 填成合法 Java package，預設 `com.example.<tlb_id 去掉所有 hyphen>`。kebab-case 的 `tlb_id`（如 `course-api`）含 hyphen，而 Java package segment 只接受 `[A-Za-z0-9_$]`、不能以數字開頭——hyphen 非法，直接帶進去會讓 Maven 專案編不過。推導時把 `-` 移除（慣例直接接合成全小寫）得 `com.example.courseapi`。若 caller payload 已明示 `base_package`，以 caller 提供者為準。

### ✅ Good

情境：tlb_id = `course-api`，caller 未提供 base_package

```
DERIVE base_package = com.example.courseapi   （course-api → courseapi）
arguments.yml: ${KICKOFF_BASE_PACKAGE} → com.example.courseapi
```

### ❌ Bad

```
${KICKOFF_BASE_PACKAGE} → com.example.course-api
（'-' 非法 Java package 字元 → 編譯失敗）
```

**預期改法**
- 對 tlb_id 做 `replace('-', '')` 再前綴 `com.example.` → `com.example.courseapi`；caller 有給 base_package 則逕用。
