# 14→15 视图 / QWeb / 前端映射表（源码核对版）

> 来源：`OCA Migration to version 15.0` 官方指南 + odoo/odoo 提交 01875541b1a8。
> 作用域：仅 14→15。14→15 的前端/模板改动是本版本对头号断裂。

## 1. QWeb `t-raw` → `t-out` / `t-esc`  — CONFIRMED

- 14.0：`t-raw` 原样输出（不转义）。
- 15.0：`t-raw` **移除**；用 `t-out`（不转义，等价 t-raw）或 `t-esc`（HTML 转义）。
- 服务端信任 HTML：`markupsafe.Markup(html)`，配合 `t-out` 不双重转义。
- 扫描 id：`t-raw`（正则 `t-raw`）。提交：odoo/odoo 01875541b1a8。

## 2. ES 模块改名 `.esm.js`  — CONFIRMED

- 以 `/** @odoo-module **/` 开头的 JS（ES module）必须改名 `*.esm.js`，并更新资产引用。
- 扫描 id：`odoo-module-esm`（正则 `@odoo-module` 在 `.js` 且文件名非 `.esm.js`）。

## 3. 资产声明进 `__manifest__.py` 的 `assets` 键  — CONFIRMED

- 15.0 起 JS/SCSS 链接从 XML 模板移入 manifest `assets` 键；**移除 `qweb` 键**（QWeb `.xml` 进 `web.assets_qweb`）。
- 路径相对仓库根目录（非模块目录）；支持 glob。
- 扫描 id：`qweb-key`（正则 `'qweb'` 在 `__manifest__.py`）。

## 4. `ir.model*` 访问移除（见 orm-api.md）

- 15.0 移除对 `ir.model`/`ir.model.fields`/`ir.model.data` 的直接访问（#69120）。详细映射见 orm-api.md。

## 红线（勿套用更晚版本）

- `attrs`/`states` 硬拒 → 16→17；`tree`→`list` → 17→18；`name_get` 移除 → 17→18；
- `get_resource_path`→`file_path` → 16→17；`t-raw` 的"重命名"本身属 14→15（已在本表）。
