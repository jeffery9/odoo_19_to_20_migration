# 9→10 模块 / 模型 / 字段 映射表（源码核对版）

> 来源：OCA `Migration to version 10.0` + Odoo 10.0 源码核对。
> 作用域：仅 9→10。**模块层无大规模重命名**（`account.invoice`→`account.move` 属 12→13）。

## 1. 模型 / 字段改名（9→10）  — CONFIRMED

| 9.0 | 10.0 | 备注 |
|---|---|---|
| `from openerp` / `import openerp` | `from odoo` / `import odoo` | 见 orm-api.md 第 1 节 |
| 清单文件 `__openerp__.py` | `__manifest__.py` | 见 orm-api.md 第 2 节 |
| 字段 `select = True` / `select=1` | `index = True` | 见 orm-api.md 第 3 节 |
| `copy` 方法 `@api.one` | `@api.multi` | 见 orm-api.md 第 4 节 |
| `base.group_configuration` | `base.group_system` | 见 security.md 第 1 节 |
| `base.group_sale_*` / `base.group_hr_*` 等 | `sales_team.*` / `hr.*` | 见 security.md 第 2 节 |

## 2. 模块重命名  — CONFIRMED（无）

9→10 没有需要改 `depends` 的模块改名。模块改名（`sale`→`sale_management` 等）属 10→11，不属本卷。

## 3. 红线

- `account.invoice`→`account.move` → 12→13；`customer/supplier`→`customer_rank/supplier_rank` → 12→13；
- `src_model`→`binding_model_id` → 12→13；`stock.quant` qty→quantity → 12→13；
- `sale`→`sale_management`、`account_accountant`→`account_invoicing` → 10→11；
- `payment.acquirer`→`payment.provider` → 15→16。
