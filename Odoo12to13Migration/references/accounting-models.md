# 12→13 会计 / 伙伴 / 税务模型映射表（源码核对版）

> 来源：`OCA Migration to version 13.0` + Odoo "accounting-pocalypse" 提交（shuzhiduo / Odoo 论坛）+ 13.0 源码核对。
> 作用域：仅 12→13。会计模型合并是本版本对头号断裂。

## 1. `account.invoice` / `.line` / `.tax` → `account.move` / `account.move.line`  — CONFIRMED

- `account.invoice` → `account.move`，用 `move_type` 区分（out_invoice / in_invoice / out_refund /
  in_refund / out_receipt / in_receipt）；`is_invoice()` 辅助判断。
- `account.invoice.line` → `account.move.line`；`invoice_id` 字段 → `move_id`。
- `account.invoice.tax` → `account.move.line`，用 `tax_line_id` 关联字段标识税行。
- `account.voucher` / `account.voucher.line` → `account.move` / `account.move.line`（`*_receipt` 类型）。
- 扫描 id：`account-invoice`（正则 `account\.invoice|account\.voucher|action_invoice_open`）。

## 2. `account.invoice.confirm` / `.refund` 向导 → 方法  — CONFIRMED

- `account.invoice.confirm` → `account.move.post()`。
- `account.invoice.refund` → `account.move.reversal`（同选项反向）。

## 3. `account.move` / `account.move.line` 自身改名  — CONFIRMED

- `account.move.amount` → `account.move.amount_total`。
- `account.move.reverse_entry_id` → `account.move.reversed_entry_id`。
- `account.move.line` 新增 `display_type`（业务查询须排除）、`exclude_from_invoice_tab`
  （发票行子集）、`tax_line_id`（税行子集）。

## 4. 关键字段映射（invoice → move）  — CONFIRMED

| invoice 字段 | move 字段 |
|---|---|
| number | name |
| reference | ref |
| comment | narration |
| user_id | invoice_user_id |
| date_invoice | invoice_date |
| date_due | invoice_date_due |
| payment_term_id | invoice_payment_term_id |
| partner_bank_id | invoice_partner_bank_id |
| cash_rounding_id | invoice_cash_rounding_id |

## 5. `res.partner` `customer` / `supplier` → `customer_rank` / `supplier_rank`  — CONFIRMED

- 布尔 → 整数 rank（可累计）。`domain` 由 `('customer','=',True)` 改为 `('customer_rank','>',0)`。
- 扫描 id：`partner-rank`（正则 `\.customer\b|\.supplier\b` 配合 res.partner 上下文，建议人工复核）。

## 6. `account.tax` `type` → `type_tax_use`  — CONFIRMED

- `account.tax.type`（sale/purchase）→ `type_tax_use`（sale/purchase/none）。

## 7. 关联改动（invoice_ids）  — CONFIRMED

- `sale.order.invoice_ids` / `pos.order.invoice_id` 现在指向 `account.move`
  （`sale.order.invoice_ids` 仍为 Many2many，comodel 改为 `account.move`）。

## 红线

- `payment.acquirer` → `payment.provider` → 15→16；`coupon` → `loyalty` → 15→16；
- `stock.production.lot` → `stock.lot` → 15→16。
