# 10→11 视图 / QWeb / 前端 映射表（源码核对版）

> 来源：Odoo 11 Release Notes + 社区前端经验 + 11.0 源码核对（Bootstrap/OWL 前代框架）。
> 作用域：仅 10→11。大规模 QWeb 重写（`t-raw` 移除、`ir.model*` 访问移除、资产进 manifest）属 14→15，不在本表。

## 1. 视图 / QWeb 变更  — CONFIRMED（温和）

- 视图结构 10→11 基本兼容；`<form>`/`<tree>`/`<field>` 等标签无破坏性改动。
- QWeb 模板（`t-*` 指令）沿用；`t-raw` 移除发生在 14→15，本卷不涉及。
- 报表模板（QWeb）的 **调用接口** 改动见 `orm-api.md` 第 4 节（`render_html`→`get_report_values`）。

## 2. 前端 / 静态资源  — CONFIRMED（含 [verify]）

- 同目录静态资源相对引入在 Python 3 下更严格；JS/CSS/SCSS 内 `import` 须为相对路径。
- Bootstrap 在前端升级（具体大版本号 `[verify]`，无官方 10→11 前端清单，以 11.0 源码 `package.json` / `web` 资产为准）。
- 11.0 处于 OWL 之前的第一代 JS 框架重构期，组件写法变动但 `t-*` 指令语义保持。

## 3. 红线

- `invisible`/`readonly` 动态表达式 → `attrs` 硬拒 → 16→17；
- `<tree>`→`<list>` → 17→18；`name_get` 移除 → 17→18；
- `t-raw` 移除 / `ir.model*` 移除 / 资产进 manifest → 14→15；
- `on_change` 属性 → `@api.onchange` 引入于 8.0（10→11 已存在，无需改动）。
