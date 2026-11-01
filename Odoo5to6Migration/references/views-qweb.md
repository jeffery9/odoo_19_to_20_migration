# 5→6 视图 / QWeb / 前端 映射表（源码核对版）

> 来源：OpenERP 6.0 发布说明 + 社区前端经验 + 6.0 源码核对。
> 作用域：仅 5→6。大规模 QWeb / 视图重写（`<tree>`→`<list>`、`t-raw` 移除、
> 资产进 manifest）属更晚版本，不在本表。

## 1. 新默认 web client  — CONFIRMED（[verify]-light）

- 6.0 引入新的默认 **web client**（GTK 客户端仍可用）。自定义模块若提供
  web 客户端资源，应放入模块下 `static/`（见 models-mapping.md 第 3 节）。
- 这是 [verify]-light 的框架级变更：6.0 的 web 客户端与 7.0+ 的 `web` 模块
  架构差异较大，勿把更晚版本约定套用到 5→6。

## 2. 视图结构  — CONFIRMED（基本兼容）

- 5.0/6.0 的视图（`arch` 内嵌 XML 的 `<form>` / `<tree>` / `<field>`）基本兼容；
  5→6 无破坏性视图改动。
- 具体 5→6 的 widget / 视图继承差异属 [verify]，以 6.0 源码 `addons/base/` 为准。

## 3. 红线

- `<tree>`→`<list>` → 17→18；`name_get` 移除 → 17→18；
- `t-raw` 移除 / `ir.model*` 移除 / 资产进 manifest → 14→15；
- `attrs`/`states` 硬拒 → 16→17；
- `invisible`/`readonly` 动态表达式迁移不属 5→6。
