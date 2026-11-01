# 8→9 HTTP / RPC / 邮件 / 二进制 映射表（源码核对版）

> 来源：8.0/9.0 源码核对 + Odoo 官方 RPC 文档。
> 作用域：仅 8→9。本卷区间这些子系统**基本不变**。

## 1. HTTP / 控制器  — CONFIRMED（不变）

- 包仍是 `openerp`：`from openerp import http`；`http.Controller`、`http.route()` 接口 8→9 无破坏性变更。
- XML-RPC / JSON-RPC 对外接口稳定。
- 注意：`openerp`→`odoo` 包改名发生在 9→10，不属于本卷（8/9 都用 `openerp`）。

## 2. 邮件 / 模板  — CONFIRMED（不变）

- `mail.template` 渲染仍用 QWeb；Jinja/Python-format 语法移除发生在 14→15，不属本卷。
- `message_post` / `message_subscribe` 接口稳定。

## 3. 二进制字段  — CONFIRMED（不变）

- `Binary` 默认存 `ir.attachment` 的时机在 13.0；8→9 维持原状（`attachment=False` 默认）。
- `fields.Binary` 用法不变。

## 4. 异常体系连带影响  — CONFIRMED

- 若 `http` / `mail` 相关代码使用了 `osv.except_osv` / `except_orm` 报错，按 orm-api.md 第 1 节改为 `openerp.exceptions.UserError`。

## 5. 红线

- `t-raw` / Jinja 邮件渲染 → 14→15；`subtype_xmlid` → 14→15；
- 控制器 `openerp.http`→`odoo.http` 改名属 9→10。
