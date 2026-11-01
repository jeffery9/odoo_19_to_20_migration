# 13→14 ORM / 模型 API 映射表（源码核对版）

> 来源：`OCA Migration to version 14.0` 官方指南 + 14.0 源码核对（commit 1f48130 等）。
> 作用域：仅 13→14。更晚改动（`name_get` 移除、`ir.model*` 访问移除）不在本表。

## 1. `_name_search` 返回 ids 列表  — CONFIRMED

- 13.0：覆写 `_name_search` 可返回 `(id, name)` 元组列表。
- 14.0：`_name_search` **必须返回 id 列表**（不再返回 name_get 风格元组）。
- 替代：返回 `self.search(...).ids`。
- 扫描 id：`name-search`（正则 `_name_search`）。源码：odoo/odoo commit 1f48130。

## 2. `_compute_display_name` 覆盖 → 改用 `name_get`  — CONFIRMED

- 14.0 自定义 `display_name` 应覆写 `name_get` 并加 `@api.depends`（对应计算字段）。
- 若要 stored `display_name`，覆写 `name_search`。
- 扫描 id：`compute-display-name`（正则 `_compute_display_name`）。

## 3. `with_context(force_company=...)` → `with_company(...)`  — CONFIRMED

- 14.0 弃用 `force_company`；改用 `self.with_company(company)`。
- 注：`with_company()` 在 **13.0 引入**，14.0 才弃用 `force_company`。
- 扫描 id：`force-company`（正则 `force_company`）。

## 4. 记录规则移除全局字段赋值行  — CONFIRMED

- 记录规则中针对 computed `global` 字段的全局赋值行需移除（该字段现在 computed）。

## 红线（勿套用更晚版本）

- `name_get` **移除** → 17→18；`ir.model*` 访问移除 → 14→15；
- `attrs`/`states` 硬拒 → 16→17；`tree`→`list` → 17→18；
- `SavepointCase`/`Environment.manage` 移除 → 14→15（14.0 仍可用）。
