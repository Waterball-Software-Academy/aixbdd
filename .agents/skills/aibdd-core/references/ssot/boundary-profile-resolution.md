# Boundary Profile Resolution

Boundary profile 合併規則的 SSOT。讀路徑（取 specifier 值）消費者各自照本檔就地做。

## 兩個來源（優先序）

1. Project override（優先）：`${BOUNDARY_YML}` 的 `profile_overrides.<specifier>`（選填）。
2. Base preset（fallback）：`aibdd-core/assets/boundaries/<type>/profile.yml` 的同名 `<specifier>` block；`<type>` 取自 `${BOUNDARY_YML}` 的 `type`，宣告 `{skill, format, semantics?, output_dir_key, default_filename}`。

## 解析取值

對每個需要的 `$specifier`（如 `state_specifier`、`operation_contract_specifier`）：

1. PARSE `${BOUNDARY_YML}`。
2. IF `profile_overrides.$specifier` 存在 → 直接使用該 block（整塊；不 merge、不讀 preset）。
3. ELSE（`profile_overrides` 無此 specifier）：
   1. 取 `${BOUNDARY_YML}` 的 `type`；缺則 STOP。
   2. READ `aibdd-core/assets/boundaries/<type>/profile.yml`；檔缺則 STOP。
   3. 取 preset 的 `$specifier` block。
