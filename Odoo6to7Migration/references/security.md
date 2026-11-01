# 6→7 安全与 `res.groups`（6→7 不变）

> 来源：OpenERP 7.0 源码核对 —— 安全/访问权机制在 6→7 **无任何破坏性变更**。
> 作用域：仅说明"本版本不需要改安全文件"，并给出更晚版本的红线以免误用。
> 注：6/7 使用 `openerp` 包名（不是 `odoo`）。

## 1. 不变项（CONFIRMED）

- `security/ir.model.access.csv`：访问权 CSV 列（`id`, `name`, `model_id:id`, `group_id:id`, `perm_read`/`perm_write`/`perm_create`/`perm_unlink`）在 6/7 完全一致，无需改动。
- `ir.rule`：记录规则写法一致（`domain_force`、全局规则 `global` 语义同 6.0）。
- `res.groups`：`groups` 字段、`implied_ids` 继承链、`category_id` 机制一致。
- 安全 XML（`<record model="ir.model.access"/>`、`<record model="res.groups"/>`）无需改动。
- 包名仍是 `openerp`（6/7 均用 `openerp`，`openerp`→`odoo` 改名是 9→10）。

## 2. 红线（勿套用更晚版本的安全改动）

- `res.groups` **privilege 模型**（group 显式声明 privilege）—— **18→19**，不在 6→7。
- `ir.access.csv` 显式访问权文件拆分 —— **19→20**，不在 6→7。
- 9→10 的 group 模块化（如 `base.group_sale_salesman` 拆分到 `sales_team.*`）—— **9→10**，不在 6→7。
- EE 安全微调（企业版 group 重组）—— 18→19 量级，不在 6→7。

## 3. `[EE-verify]`

- Enterprise 7.0 的 group 继承链若有微调，需对照 EE 7.0 树复核；社区版无变化。
