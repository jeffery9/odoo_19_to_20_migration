# 11→12 安全与 `res.groups`（11→12 不变）

> 来源：OCA 12.0 迁移指南核对 —— 安全/访问权机制在 11→12 **无任何破坏性变更**。
> 作用域：仅说明"本版本对不需要改安全文件"，并给出更晚版本的红线以免误用。

## 1. 不变项（CONFIRMED）

- `ir.model.access.csv`：访问权 CSV 格式在 11/12 完全一致，无需改动。
- `ir.rule`：记录规则写法一致（`domain_force`、全局规则 `global` 语义同 11）。
- `res.groups`：`groups` 字段、`implied_ids` 继承链、`category_id` 机制一致。
- 安全 XML（`<record model="ir.model.access"/>`、`<record model="res.groups"/>`）无需改动。

## 2. 红线（勿套用更晚版本的安全改动）

- `res.groups` **privilege 模型**（group 显式声明 privilege）—— **18→19**，不在 11→12。
- `ir.access.csv` 显式访问权文件拆分 —— **19→20**，不在 11→12。
- EE 安全微调（企业版 group 重组）—— 18→19 量级，不在 11→12。

## 3. `[EE-verify]`

- Enterprise 12.0 的 group 继承链若有微调，需对照 EE 12.0 树复核；社区版无变化。
- 本工作台对 11→12 不单列 EE 专属改动（企业版大改在 18→19）。
