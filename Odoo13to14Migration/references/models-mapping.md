# 13→14 字段属性 / 数据模型映射表（源码核对版）

> 来源：`OCA Migration to version 14.0` 官方指南 + 14.0 源码核对（commit f0481392）。
> 作用域：仅 13→14。

## 1. `selection_add` 必须带 `ondelete=`  — CONFIRMED

- 14.0 起 `selection_add` 追加选项时必须为每个旧值指定卸载处理。
- 例子：`selection_add=[("foo","Foo")], ondelete={"foo": "set null"}`。
- 扫描 id：`selection-ondelete`（正则 `selection_add=`）。源码：odoo/odoo commit f0481392。

## 2. `Char` 字段移除 `size=X` 属性  — CONFIRMED

- 14.0 `fields.Char(size=16)` 的 `size` 不再限制字符串长度（被忽略）。
- 扫描 id：`char-size`（正则 `fields\.Char\([^)]*size\s*=`）。

## 3. `string` 属性在列表视图显示为文本  — CONFIRMED（轻微）

- 14.0 起 `<field string="x">` 在 list 视图直接显示为文本（非 tooltip）；建议改用 `title` 属性。

## 4. 库存字段改名（[verify]）

- `stock.picking.move_lines` → `move_ids_without_package`；`move_line_ids` → `move_line_ids_without_package`。
- 属 14.0 库存重构，但 OCA 14.0 核心指南未逐条列；建议 14.0 源码（`stock.picking`）核对后固化。

## 清单（含可信度）

| 13.0 | 14.0 | 类别 | 可信度 |
|---|---|---|---|
| `selection_add=[...]` 无 ondelete | `+ ondelete={...}` | 字段属性 | CONFIRMED |
| `fields.Char(size=16)` | 移除 `size` | 字段属性 | CONFIRMED |
| `<field string>` list 显示 tooltip | 显示文本（用 title） | 视图属性 | CONFIRMED |
| `stock.picking.move_lines` | `move_ids_without_package` | 字段改名 | [verify] |
| `stock.picking.move_line_ids` | `move_line_ids_without_package` | 字段改名 | [verify] |
