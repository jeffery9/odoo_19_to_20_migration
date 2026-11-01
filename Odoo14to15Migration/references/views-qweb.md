# 14→15 视图 / QWeb / 前端映射表（源码核对版）

> 来源：Odoo CE 14.0 / 15.0 源码树复核（`odoo/addons/base/models/qweb.py`、`web` 模块资产机制）。
> 作用域：仅 14→15。前端/模板是本版本对的头号断裂面。

## 1. QWeb 指令：`t-raw` / `t-esc` → `t-out`  — CONFIRMED

- 14.0：`t-raw` 原样输出（不转义）；`t-esc` 转义。
- 15.0：两者都**标记 deprecated**（仍渲染，每次渲染写 warning），**16.0 才彻底移除**。
- `t-out` 编译为 `escape(content)`：**默认转义**，只有 `markupsafe.Markup` 实例不转义。
  `t-raw` 分支在 15.0 内部会 `content = Markup(content)` 来保住旧的「不转义」语义——照搬替换拿不到这个补偿。
- 因此：
  - `fields.Html` 值（`body_html`/`description`/`narration`/`comment`）→ 直接 `t-out`，仍不转义；
  - `Char`/`Text` 值 → `t-out` 会转义，确实要输出 HTML 时包 `Markup(...)`。
- 扫描 id：`t-raw`（正则 `t-raw`）、`t-esc`（正则 `t-esc`）。
- 校验：只 warning，须开 `--dev=all` 才看得到；不要指望加载报错。

## 2. ES 模块改名 `.esm.js`  — CONFIRMED

- 以 `/** @odoo-module **/` 开头的 JS（ES module）必须改名 `*.esm.js`，并更新资产引用。
- 扫描 id：`odoo-module-esm`（正则 `@odoo-module` 在 `.js` 且文件名非 `.esm.js`）。

## 3. 资产声明进 `__manifest__.py` 的 `assets` 键  — CONFIRMED

- 14.0：官方模块**没有一个**用 `assets` 键，全部走 XML `<template>` + manifest `qweb` 键（77 个模块在用）。
- 15.0：179 个模块用 `assets` 键；`qweb` 键**被静默忽略**（不报错，模板因此不加载）。
- 旧写法 `<template id="assets_backend" inherit_id="web.assets_backend">` 不再生效。
- 路径相对仓库根目录（非模块目录）；支持 glob。
- 新增 `ir.asset` 模型承接资产记录，可替代自定义 `assets_*.xml`。
- 扫描 id：`qweb-key`（正则 `'qweb'` 在 `__manifest__.py`）、`xml-asset-tag`（XML 里的 `<script src=...>` / `<link rel="stylesheet">`）。

## 4. 数据 API 侧（详见 orm-api.md）

- `ir.model.data` 的 `xmlid_lookup`/`xmlid_to_*` 私有化，`_get_id`/`get_object_reference` 移除。
- **「15.0 移除 `ir.model*` 直接访问」不成立**——`ir.model` / `ir.model.fields` 的正常读取不受影响。

## 红线（勿套用更晚版本）

- `attrs`/`states` 硬拒 → 16→17；`tree`→`list` → 17→18；`name_get` 移除 → 17→18；
- `get_resource_path`→`file_path` → 16→17；
- `t-raw` 的**彻底移除** → **15→16**（15.0 只是弃用，本表处理的是「改用 t-out」，不是「救一个报错」）。
