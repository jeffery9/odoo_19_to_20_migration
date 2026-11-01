# 14→15 ORM / 模型 API / 测试映射表（源码核对版）

> 来源：`OCA Migration to version 15.0` 官方指南 + odoo/odoo 提交 #69120 / #62031。
> 作用域：仅 14→15。

## 1. `ir.model*` 对象访问移除  — CONFIRMED

- 15.0 移除对 `ir.model` / `ir.model.fields` / `ir.model.data` / `ir.model.fields.selection` 的直接访问。
- 修复：用 `sudo()` 后访问，或优先用模型自身 API（`_fields`、`_xmlid_lookup()`、`_get_id()`）。
- 源码：odoo/odoo#69120。
- 扫描 id：`ir-model-access`（正则 `env\[['\"]ir\.model|self\.env\[['\"]ir\.model|env\.ref\(['\"]ir\.model`）。
- 注：与 13→14 的 `ir.actions.*` 访问移除是**不同对象**（14 限 actions.*，15 限 model*）。

## 2. `SavepointCase` → `TransactionCase`  — CONFIRMED

- 15.0 移除 `SavepointCase` 别名（与 `TransactionCase` 行为相同）。
- 替代：直接用 `TransactionCase`。
- 扫描 id：`savepoint-case`（正则 `SavepointCase`）。提交：odoo/odoo#62031。

## 3. `Environment.manage()` 不再需要  — CONFIRMED

- 15.0 起创建新 Environment 不再需要 `with Environment.manage():` 上下文。
- 扫描 id：`env-manage`（正则 `Environment\.manage`）。

## 红线（勿套用更晚版本）

- `name_get` **移除** → 17→18；`attrs`/`states` 硬拒 → 16→17；`tree`→`list` → 17→18；
- `SavepointCase`/`Environment.manage` **移除是 15.0**（非更晚版本，本版本对即处理）。
