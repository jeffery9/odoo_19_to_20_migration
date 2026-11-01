# 12→13 视图 / QWeb / 前端映射表（源码核对版）

> 来源：`OCA Migration to version 13.0` + shine-it《如何升级到odoo13》+ 13.0 源码核对。
> 作用域：仅 12→13。12→13 的 XML 视图改动较小（动作绑定 + view_type 移除）；`attrs`/`states`/`tree` 均保留。

## 1. 动作窗口 XML 移除 `view_type`  — CONFIRMED

- 12.0：`<field name="view_type">form</field>` 冗余（自 11.0 起 tree 已不支持）。
- 13.0：直接删除（始终 form）。
- 扫描 id：`view-type`（正则 `view_type`）。

## 2. `ir.actions.act_window` 移除 `multi` 字段 → `binding_view_types`  — CONFIRMED

- 12.0：`<field name="multi">True</field>` 指示动作在哪些视图出现。
- 13.0：改为 `<field name="binding_view_types">list</field>`（list / form / 空=两者）。
- 快捷标签：`<act_window ... binding_views="form"/>`。
- 扫描 id：`act-window-multi`（正则 `<field name="multi">`）。

## 3. `src_model` → `binding_model_id`（13.0 仍兼容，13→14 收紧）  — CONFIRMED

- 12→13 阶段 `src_model` 字段尚可直接使用；新写动作建议用 `binding_model_id` 面向 13→14 兼容。
- 完整访问移除见 13→14 烹饪书（OCA 14.0）。

## 4. 前端依赖（中等断裂）  — [verify]

- FontAwesome 5 图标改名：`area-chart`→`chart-area`、`address-book-o`→`address-book` 等。
- **JavaScript：jQuery Promise (`$.Deferred`) → 原生 `Promise`**（OCA 13.0 明确要求）。
- jQuery 3.x / Bootstrap 4.x 就位；更大前端跃进（Owl / `t-raw` 移除）在 **14→15**。

## 红线

- `attrs`/`states` 硬拒 → 16→17；`tree`→`list` → 17→18；`t-raw` 移除 → 14→15；
- `invisible`/`readonly` 动态表达式收紧（仅 context 直查可用）→ 13→14。12→13 全部保留旧写法。
