# 14→15 安全与 `res.groups`（14→15 不变）

> 来源：OCA 15.0 迁移指南核对 —— 安全/访问权机制在 14→15 **无破坏性变更**。
> 作用域：仅说明"本版本对不需要改安全文件"，并给出更晚版本的红线以免误用。

## 1. 不变项（CONFIRMED）

- `ir.model.access.csv`：访问权 CSV 格式在 14/15 完全一致，无需改动。
- `ir.rule`：记录规则写法一致（`domain_force`、全局规则语义同 14）。
- `res.groups`：`groups` 字段、`implied_ids` 继承链、`category_id` 机制一致。
- 安全 XML 无需改动。
- 注：15.0 访问 `ir.model*` 受限（见 orm-api.md），但**不影响** `ir.model.access` 的正常写法。

## 2. 红线（勿套用更晚版本的安全改动）

- `res.groups` **privilege 模型** —— **18→19**，不在 14→15。
- `ir.access.csv` 显式访问权文件拆分 —— **19→20**，不在 14→15。
- EE 安全微调（企业版 group 重组）—— 18→19 量级，不在 14→15。

## 3. `[EE-verify]`

- Enterprise 15.0 的 group 继承链若有微调，需对照 EE 15.0 树复核；社区版无变化。
