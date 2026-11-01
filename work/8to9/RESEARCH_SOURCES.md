# 8→9 研究来源与源码核实地图

> 本文件记录 8→9 每条破坏性变更的溯源与核实状态，供修订时复核。

## 已核实（CONFIRMED）

| 变更 | 来源 | 核实方式 |
|---|---|---|
| 9.0 引入 Community / Enterprise 版本拆分 | Odoo 9.0 Release Notes (2015) | Release Notes 明确"Odoo now ships Community and Enterprise" |
| `account_voucher` / `account_analytic_plan` / `document` / `marketing` 等模块变 Enterprise-only | Odoo 9.0 Release Notes + oejia.net 升级分析 | "several modules moved to the Enterprise edition"；EE 树核对 [EE-verify] |
| `osv.except_osv` / `except_orm` → `openerp.exceptions.UserError` | oejia.net《Odoo 8 到 9 升级分析》 | 异常体系切换示例 |
| `ir.model` `osv_memory` 字段 → `transient` | oejia.net 升级分析 + 9.0 源码核对 | `ir_model` 字段名变更 |
| `ir.model` 方法 `_is_osv_memory` / `_search_osv_memory` 移除 | 9.0 源码核对 | 方法在 9.0 不存在 |
| `osv_memory_autovacuum` 模型 → `ir_autovacuum` | 9.0 源码核对 | 模型改名 |
| `ir.cron` 新增 `method_direct_trigger` | 9.0 源码核对 | 增量，非破坏 |
| 8.0 / 9.0 均使用 `from openerp import ...`（`openerp`→`odoo` 属 9→10） | 8.0/9.0 源码核对 | 包名未改 |
| `@api.one` / `@api.multi` / `@api.model` 在 8.0 已存在（移除属 11→12） | 8.0 源码核对 | New API 已就位 |
| 9.0 无 `odoo/upgrade_code/` / `openerp/upgrade_code/` 模块（引擎 18.0 才出现） | odoo/odoo 仓库核查 | codemod 引擎可用性 |

## 待核实（[verify] / [EE-verify]）

| 变更 | 状态 | 备注 |
|---|---|---|
| Material Design 具体落地细节（类名变化、SCSS 变量） | [verify] | 无官方 8→9 前端清单；以 9.0 源码 `web` 模块资产为准 |
| 变为 Enterprise-only 的完整模块清单及 XML-ID 去向 | [EE-verify] | 企业版 9.0 的 module 列表需对照 EE 树逐项确认 |

## 版本作用域红线（已对照确认不属于 8→9）

- `openerp`→`odoo` 包改名 / `__openerp__.py`→`__manifest__.py` / group 模块化 —— **9→10**
- `@api.one` 移除 / `fields.Date` 对象化 / `parent_path` / `ir.actions.act_window.view` 移除 —— **11→12**
- New-API 装饰器、`self.env`、`osv.Model`→`models.Model` —— **7→8**
- `account.invoice`→`account.move` —— **12→13**
