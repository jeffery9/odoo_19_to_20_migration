# 13→14 安全与 `res.groups`（13→14 不变；TransientModel 需显式 ACL）

> 来源：OCA 14.0 迁移指南核对 —— 安全/访问权机制在 13→14 **无破坏性变更**（除向导 ACL）。
> 作用域：仅说明"本版本对基本不改安全文件"，并给出更晚版本的红线以免误用。

## 1. 不变项（CONFIRMED）

- `ir.model.access.csv`：访问权 CSV 格式在 13/14 完全一致，无需改动。
- `ir.rule`：记录规则写法一致（`domain_force`、全局规则语义同 13）。
- `res.groups`：`groups` 字段、`implied_ids` 继承链、`category_id` 机制一致。
- 安全 XML 无需改动。

## 2. TransientModel 需显式 ACL（CONFIRMED，新增要求）

- 14.0 起向导（`TransientModel`）**需要显式安全 ACL**（及可选记录规则），不能再隐式访问。
- 在 `security/ir.model.access.csv` 为向导模型补一行访问权。

## 3. 红线（勿套用更晚版本的安全改动）

- `res.groups` **privilege 模型** —— **18→19**，不在 13→14。
- `ir.access.csv` 显式访问权文件拆分 —— **19→20**，不在 13→14。
- EE 安全微调（企业版 group 重组）—— 18→19 量级，不在 13→14。

## 4. `[EE-verify]`

- Enterprise 14.0 的 group 继承链若有微调，需对照 EE 14.0 树复核；社区版无变化。
