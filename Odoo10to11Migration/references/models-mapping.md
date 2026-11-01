# 10→11 模块 / 模型 / 字段 映射表（源码核对版）

> 来源：Odoo 论坛 v10→v11 经验帖（Anil Kesariya / Niyas Raphy）+ OCA 10.0 指南 + 11.0 源码。
> 作用域：仅 10→11。**模型层无大规模重命名**（`account.invoice`→`account.move` 属 12→13）。

## 1. 模块改名  — CONFIRMED

| 10.0 | 11.0 | 备注 |
|---|---|---|
| `sale` | `sale_management` | 销售模块改名 |
| `account_accountant` | `account_invoicing` | 会计辅助改名 |

- `depends` 列表需同步：`sale` → `sale_management`。
- 扫描 id：`module-rename`（正则 `account_accountant|\bsale\b(?!\w*_management)` 谨慎匹配，或 `depends` 中出现旧名）。

## 2. 模块合并  — CONFIRMED

| 被合并（10.0） | 并入（11.0） | 备注 |
|---|---|---|
| `account_tax_cash_basis` | `account` | 现金会计制度并入 account |
| `report` | `web` | report 模块并入 web |

- 合并后 XML-ID 前缀随之迁移（如 `report.*` action 可能移到 `web` 或业务模块），需逐条核对。
- 扫描 id：`module-merge`（正则 `account_tax_cash_basis|\breport\b` 出现在 depends/import，非 web.report 调用）。

## 3. 模型 / 字段改名  — CONFIRMED

| 10.0 | 11.0 | 备注 |
|---|---|---|
| `ir.cron.model`（字符串 eval） | `ir.cron.model_id`（ref ir.model） | 见 orm-api.md 第 5 节 |
| `workflow` / `wkf` 模型 | 移除 | 见 orm-api.md 第 3 节 |
| `base.group_configuration` | `base.group_system` | 见 security.md |

## 4. 红线

- `account.invoice`→`account.move` → 12→13；`customer/supplier`→`customer_rank/supplier_rank` → 12→13；
- `src_model`→`binding_model_id` → 12→13；`stock.quant` qty→quantity → 12→13；
- `payment.acquirer`→`payment.provider` → 15→16。
