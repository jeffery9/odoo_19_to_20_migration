# 11→12 ORM / 模型 API 映射表（源码核对版）

> 来源：`OCA Migration to version 12.0` + 社区（Cybrosys / 掘金 / CSDN / Oejia）+ 12.0 源码核对。
> 作用域：仅 11→12 破坏性变更。更晚改动（`name_get` 移除、`get_resource_path`→`file_path`、`attrs` 硬拒、
> `account.move` 重写、`customer_rank`）一律不在本表。

## 1. `@api.one` 移除  — CONFIRMED

- 11.0：`@api.one` 自动拆 `self` 为单条并循环，返回结果是列表。
- 12.0：`@api.one` 已移除。模型方法默认多记录语义（旧 `api.multi`）。
- 替代：`def meth(self, ...): for record in self: ...`（或纯模型方法加 `@api.model`）。
- `@api.multi` 在 12.0 仍存在但弃用——建议直接省略或 `@api.model`。
- 扫描 id：`api-one`。

## 2. `fields.Date` / `fields.Datetime` 运行时对象化  — CONFIRMED

- 11.0 及更早：字段运行时是字符串，需 `fields.Date.from_string()` / `to_string()`。
- 12.0：字段运行时是真实 `date` / `datetime` 对象；`from_string` 已移除。
- 替代：`fields.Date.to_date(str)` / `fields.Datetime.to_datetime(str)`（12.0 新增）。
- `to_string` 仍可用于写回字符串，但大多场景不再需要。
- 扫描 id：`date-from-string`（正则 `\.from_string\s*\(`）。

## 3. `@api.model_create_multi`（12.0 新增）  — CONFIRMED

- 覆写 `create()` 必须加 `@api.model_create_multi`，`self` 为记录集，`vals_list` 为列表。
- 仅当显式 `def create` 时才需改动；仅 `super().create(...)` 前后加逻辑不受影响。

## 4. `_parent_store`：`parent_left`/`parent_right` → `parent_path`  — CONFIRMED

- 12.0 用 `parent_path = fields.Char(index=True, store=True)` 替代左右值字段。
- 删除 `parent_left`/`parent_right` 两个字段声明。
- 数据库 `parent_path` 由 OpenUpgrade `migrations/12.0/` 或 `_parent_store` 维护填充。
- 扫描 id：`parent-left-right`（正则 `parent_left|parent_right`）。

## 5. `do_notify` / `do_warning` 移除  — CONFIRMED

- 12.0 移除 `self.do_notify(msg)` / `self.do_warning(msg)`。
- 替代：`raise UserError(_("..."))` 或 `self.message_post(body=..., message_type="notification")`。
- 扫描 id：`do-notify`（正则 `\bdo_notify\b|\bdo_warning\b`）。

## 红线（勿套用更晚版本）

- `name_get` 移除 → 17→18；`get_resource_path`→`file_path` → 16→17；
- `attrs`/`states` 硬拒 → 16→17；`account.invoice`→`account.move` → 12→13；
- `customer`/`supplier`→`customer_rank`/`supplier_rank` → 12→13；`t-raw` 移除 / `ir.model*` 移除 → 14→15。
