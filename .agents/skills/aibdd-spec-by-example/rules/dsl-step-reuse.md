# DSL step 句式重用

第二輪以上的 plan，前輪 dsl-refine 已在 boundary packages 樹產出 dsl.yml（package 層 `dsl.yml` 與各 `{feature}.dsl.yml`）。草擬 Example 的 Given／When／Then 時，同語意的句子必須沿用既有 dsl_step 的 `format` 句式，不得另創同義異形句。`$DSL_CORPUS` 為空（首輪尚無任何 dsl.yml）時本檔不構成約束。

為什麼：dsl-refine 依句面對映 dsl_step。同一語意換個說法，下游只能重開一條重複的 dsl_step 或回頭澄清，DSL 語料隨輪次發散；在 SBE 源頭沿用句式，語料才收斂、既有 isa 推導才被重用。

## 約束

1. 同語意必沿用既有 format
   1. 草擬的 step 若其業務語意（動作／前置／斷言意圖與參與實體）與 `$DSL_CORPUS` 某 dsl_step 的 `format` 相同、僅具體值不同，必須以該 `format` 句式填入本 Example 的具體值，不得改語序、換同義詞、增刪修飾語另造一句。
   2. 例：語料已有 `{buyer} 下單 {qty} 件 {product}`，新 Example 寫「"小華" 下單 2 件 鍵盤」；不得寫「"小華" 購買了 2 個 鍵盤」或「"小華" 建立一筆 2 件鍵盤的訂單」。

2. 語意不同才可草擬新句式
   1. 只有既有 format 換參數值仍表達不了的語意（新動作、新前置面、新斷言面）才草擬新句式；新句式仍受 `business-language-judgments.md` 約束。
   2. 「參數值不同」「主詞不同」「數量不同」皆不構成新句式的理由——那正是 format 參數要承載的。

3. 對映不確定交澄清
   1. 一句草稿似可對上多個 dsl_step、或與某 format 似同非同（語意有無實質差異拿不準）→ 不逕行二選一、也不逕行造新句，蒐集成 `$ASK_BATCH` 交 `/clarify`，附該草稿句與候選 dsl_step 的 `format`（含來源檔路徑）作 anchor。

4. 只沿用句式，不再現值
   1. 沿用的是 `format` 的句式骨架；參數的具體值仍依 `example-value-rule.md` 取自本批次 spec 原文，不得抄語料中他處 Example 的舊值。
