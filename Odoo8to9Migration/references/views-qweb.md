# 8→9 视图 / QWeb / 前端 映射表（源码核对版）

> 来源：Odoo 9.0 Release Notes（Material Design UI）+ 8.0/9.0 源码核对。
> 作用域：仅 8→9。大规模 QWeb 重写（`t-raw` 移除、`ir.model*` 访问移除、资产进 manifest）属 14→15，不在本表。

## 1. 视图 / QWeb 变更  — CONFIRMED（温和）

- 视图结构 8→9 基本兼容；`<form>` / `<tree>` / `<field>` 等标签无破坏性改动。
- QWeb 模板（`t-*` 指令）语义保持；`t-raw` 移除发生在 14→15，本卷不涉及。
- 报表模板调用接口 8→9 无破坏性变更（报表 API 重写属 10→11）。

## 2. 前端 / 静态资源：Material Design  — CONFIRMED（含 [verify]）

- 9.0 引入 **Material Design** 风格的新 UI（Odoo 9 Release Notes 明确提及 UI 全面 Material 化）。
- 前端整体换肤；自定义 CSS / 模板若硬编码了旧样式类名，可能需要适配。
- `[verify]` Material Design 具体落地细节（类名变化、SCSS 变量）以 9.0 源码 `web` 模块资产为准；本卷仅作 UI 提示，不展开破坏性清单。

## 3. 红线

- `invisible` / `readonly` 动态表达式 → `attrs` 硬拒 → 16→17；
- `<tree>`→`<list>` → 17→18；`name_get` 移除 → 17→18；
- `t-raw` 移除 / `ir.model*` 移除 / 资产进 manifest → 14→15；
- `@api.onchange`（替代 `on_change` 属性）引入于 7→8，8→9 已存在，无需改动。
