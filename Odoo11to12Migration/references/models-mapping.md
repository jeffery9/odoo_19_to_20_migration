# 11→12 模块 / 模型 / 字段映射表（源码核对版）

> 来源：`OCA Migration to version 12.0` + 社区 + 12.0 源码核对。
> 作用域：仅 11→12。本版本对**无**重大模型重命名（account.move、customer_rank、payment.provider 均不在 11→12）。

## 11.0 → 12.0 映射总表

| 11.0 | 12.0 | 类别 | 可信度 |
|---|---|---|---|
| `@api.one` 方法 | 无装饰器 + `for record in self` | 装饰器 | CONFIRMED |
| `fields.Date.from_string(x)` | `fields.Date.to_date(x)` | 工具函数 | CONFIRMED |
| `fields.Datetime.from_string(x)` | `fields.Datetime.to_datetime(x)` | 工具函数 | CONFIRMED |
| 日期字段运行时 = 字符串 | = `date`/`datetime` 对象 | 运行时类型 | CONFIRMED |
| `ir.actions.act_window.view` 记录 | 动作 `view_ids` | 模型移除 | CONFIRMED |
| `do_notify(msg)` / `do_warning(msg)` | `raise UserError` / `message_post` | 方法移除 | CONFIRMED |
| `parent_left` / `parent_right` | `parent_path` | 字段 | CONFIRMED |
| `t-field-options` | `t-options` | QWeb 属性 | CONFIRMED |
| `Binary` 默认存 `ir.attachment`？ | 仍存字段（默认改附件是 13.0） | 字段存储 | [verify] |

## 本版本对**不涉及**的重大重命名（红线，属更晚版本）

- `account.invoice` → `account.move` —— **12→13**
- `customer` / `supplier` → `customer_rank` / `supplier_rank` —— **12→13**
- `stock.quant` `qty` → `quantity` —— **12→13** `[verify]`
- `src_model` → `binding_model` —— **12→13**
- `payment.acquirer` → `payment.provider` —— **15→16**
- `stock.production.lot` → `stock.lot` —— **15→16**
- `coupon.*` → `loyalty.*` —— **15→16**

## 数据库迁移

- 无模型/表级重命名需要 OpenUpgrade 处理（11→12 的 schema 变化很小）。
- `parent_path` 列需在 12.0 首次安装/升级时由 `_parent_store` 维护或 `migrations/12.0/` 填充。
