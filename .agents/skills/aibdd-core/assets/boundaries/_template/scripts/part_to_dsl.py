"""<boundary-id> preset's part-to-DSL plugin (authoring template).

這是 boundary preset 的核心 plugin。`/aibdd-plan` 04-dsl-synthesis 階段，
dsl_cli 會把 spec（OpenAPI / DBML / ...）parse 成 parts，再呼叫本檔的
`generate_templates(parts, context)` 把每個 part 展開成 DSL instruction template。

載入契約（由 dsl_cli/preset_loader.py 強制）：
  1. 本檔路徑固定為 `<boundaries_root>/<preset>/scripts/part_to_dsl.py`。
  2. 必須 expose 一個 `def generate_templates(parts, context)`；缺它會在 load
     階段以 PluginContractError 失敗。
  3. plugin 必須完全自含 —— 只能從 `dsl_cli.*` import，不得做 relative / sibling
     import（loader 以 spec_from_file_location 動態載入，不會把本目錄放上 sys.path）。

本 plugin 是下列事項的 SSOT（dsl_cli 的 eval_rules 不會再 re-check）：
  1. 每一種 part-kind 展開成哪些 handler。
  2. entry name 的自動產生規則（建議 `<natural-id>.<handler>`）。
  3. 每個 handler 的 candidate binding target 走哪一種 URI scheme。
這些保證若寫錯，eval 不會幫你擋；scheme 合法性是這裡構造性保證的。
"""

from __future__ import annotations

# 只從 dsl_cli.models import；可用的 part / 結構型別依你需要解析的 spec 種類挑選。
# 常見：ApiOperationPart（OpenAPI）、TablePart / RefPart（DBML）、
# CandidateBinding、DSLInstructionTemplate。新 spec 種類需先在 dsl_cli/spec_parsers/
# 加 parser 才會有對應 part。
from dsl_cli.models import (  # noqa: F401  # 依實際使用刪掉用不到的
    CandidateBinding,
    DSLInstructionTemplate,
    # ApiOperationPart,
    # TablePart,
    # RefPart,
)


def generate_templates(parts, context):
    """把 parsed parts 展開成 DSL instruction templates。

    parts   : spec_parser 產出的 part 物件序列（型別依 spec 種類而定）。
    context : 由 orchestrator 傳入的執行脈絡（boundary 名、路徑等）。
    return  : list[DSLInstructionTemplate]。
    """
    templates: list[DSLInstructionTemplate] = []
    for part in parts:
        # 依 part 種類分派到對應的 fan-out helper。
        # isinstance 比對你 import 的 part 型別，逐種展開。
        # 未知 part-kind 直接 skip：未來新增 spec_parser 時可疊加而不擾動既有 preset。
        _ = part  # 範本佔位；實作時換成 isinstance 分派，例如：
        # if isinstance(part, TablePart):
        #     templates.extend(_for_table(part))
    return templates


# --- 每種 part-kind 一個 fan-out helper ---------------------------------------
# 每個 helper 回傳 list[DSLInstructionTemplate]；每個 template 至少帶：
#   handler           : boundary 支援的 handler ID
#   name              : 全域唯一名（建議 <natural-id>.<handler>）
#   target_part_path  : 綁定的 truth 錨點（本 plugin 內 scheme 規則）
#   source_spec_path  : 來源 spec 檔
#   candidate_bindings: tuple[CandidateBinding(key=..., target=<uri-scheme:...>)]
#
# 範例（DBML table → state-builder + state-verifier）：
# def _for_table(part):
#     bindings = tuple(
#         CandidateBinding(key=c.name, target=c.target_part_path) for c in part.columns
#     )
#     builder = DSLInstructionTemplate(
#         handler="state-builder",
#         name=f"{part.table_name}.state-builder",
#         target_part_path=part.target_part_path,
#         source_spec_path=part.spec_file,
#         candidate_bindings=bindings,
#     )
#     return [builder]
