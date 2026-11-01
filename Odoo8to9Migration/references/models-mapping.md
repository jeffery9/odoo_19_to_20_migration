# 8→9 模块 / 模型 / 字段 映射表（源码核对版）

> 来源：Odoo 9.0 Release Notes（Community/Enterprise 拆分）+ oejia.net 升级分析 + 9.0 源码核对。
> 作用域：仅 8→9。**模型层无大规模重命名**（`account.invoice`→`account.move` 属 12→13）。

## 1. Community / Enterprise 版本拆分（头号断裂）  — CONFIRMED（含 [verify] / [EE-verify]）

9.0 把 Odoo 拆分为 **Community** 与 **Enterprise**。大量过去在核心的模块被移到付费的 **Enterprise** 版。对自定义模块的影响：

- 若 `depends` 了变为 Enterprise-only 的模块，该依赖现在需要 Enterprise 版。
- 部分 XML-ID / 模型随模块迁移而移动。

### 常见变为 Enterprise-only 的模块（[verify] / [EE-verify]，以 9.0 EE 树为准）

| 模块 | 去向 | 标注 |
|---|---|---|
| `account_voucher`（凭证） | Enterprise | [EE-verify] |
| `account_analytic_plan`（分析会计计划） | Enterprise | [EE-verify] |
| `document`（文档管理） | Enterprise | [EE-verify] |
| `marketing`（营销） | Enterprise | [EE-verify] |
| `crm` 部分企业特性 | Enterprise | [EE-verify] |
| `hr` 部分企业特性 | Enterprise | [EE-verify] |
| `website` 部分企业特性 | Enterprise | [EE-verify] |

- 扫描 id：`enterprise-split`（保守匹配已知集合 `account_voucher|account_analytic_plan|document|marketing`，命中即标 [verify]）。

## 2. 模型 / 字段改名  — CONFIRMED

| 8.0 | 9.0 | 备注 |
|---|---|---|
| `osv.except_osv` / `except_orm` | `openerp.exceptions.UserError` | 见 orm-api.md 第 1 节 |
| `ir.model` `osv_memory`（字段） | `transient` | 见 orm-api.md 第 2 节 |
| `ir.model` `_is_osv_memory` / `_search_osv_memory`（方法） | 移除 | 见 orm-api.md 第 2 节 |
| `osv_memory_autovacuum`（模型） | `ir_autovacuum` | 见 orm-api.md 第 3 节 |
| `ir.cron` `method_direct_trigger` | 新增（增量） | 见 orm-api.md 第 4 节 |

## 3. 红线

- `account.invoice`→`account.move` → 12→13；`customer/supplier`→`customer_rank/supplier_rank` → 12→13；
- `src_model`→`binding_model` → 12→13；`stock.quant` qty→quantity → 12→13；
- `payment.acquirer`→`payment.provider` → 15→16；
- `openerp`→`odoo` 包改名 → 9→10。
