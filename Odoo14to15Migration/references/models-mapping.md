# 14→15 字段 / 资产 / 数据映射表（源码核对版）

> 来源：`OCA Migration to version 15.0` 官方指南。
> 作用域：仅 14→15。

## 1. `t-raw` → `t-out` / `t-esc` 速查  — CONFIRMED

| 14.0 | 15.0 | 说明 |
|---|---|---|
| `<t t-raw="expr"/>` | `<t t-out="expr"/>` | 不转义（等价 t-raw） |
| `<t t-raw="expr"/>`（安全场景） | `<t t-esc="expr"/>` | HTML 转义（默认安全） |
| 服务端原始 HTML | `markupsafe.Markup(html)` + `t-out` | 避免双重转义 |

## 2. `__manifest__.py` 资产声明  — CONFIRMED

| 14.0 | 15.0 |
|---|---|
| XML `<template>` 内 `<link>`/`<script>` 资产 | 移入 manifest `assets` 键 |
| manifest 含 `'qweb': [...]` 键 | 删除；QWeb `.xml` 进 `web.assets_qweb` |
| 路径相对模块目录 | 路径相对仓库根目录（支持 glob） |

## 3. ES 模块文件改名  — CONFIRMED

| 14.0 | 15.0 |
|---|---|
| `static/src/js/foo.js`（`/** @odoo-module **/`） | `static/src/js/foo.esm.js`（并改资产引用） |

## 清单（含可信度）

| 14.0 | 15.0 | 类别 | 可信度 |
|---|---|---|---|
| `t-raw` | `t-out`/`t-esc` | 模板指令 | CONFIRMED |
| `foo.js`（`@odoo-module`） | `foo.esm.js` | 前端文件 | CONFIRMED |
| `qweb` 键 / XML 资产链接 | manifest `assets` 键 | 资产机制 | CONFIRMED |
| 路径相对模块目录 | 相对仓库根目录 | 资产路径 | CONFIRMED |

## 红线

- `payment.acquirer`→`payment.provider`、`coupon`→`loyalty`、`stock.production.lot`→`stock.lot` → 15→16；
- `ir_translation`→JSONB → 15→16；`attrs`/`states` 硬拒 → 16→17。
