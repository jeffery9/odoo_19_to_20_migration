# 9→10 HTTP / RPC / 邮件 / 二进制 映射表（源码核对版）

> 来源：9.0/10.0 源码核对 + Odoo 官方 RPC 文档。
> 作用域：仅 9→10。本卷区间这些子系统**基本不变**，仅随主改名的 `openerp.http`→`odoo.http`。

## 1. HTTP / 控制器  — CONFIRMED（随主改名）

- 随包改名：`from openerp import http` → `from odoo import http`；`http.Controller`、`http.route()` 接口 9→10 无破坏性变更。
- XML-RPC / JSON-RPC 对外接口稳定。

## 2. 邮件 / 模板  — CONFIRMED（不变）

- `mail.template` 渲染仍用 QWeb；Jinja/Python-format 语法移除发生在 14→15，不属本卷。
- `message_post` / `message_subscribe` 接口稳定。

## 3. 二进制字段  — CONFIRMED（不变）

- `Binary` 默认存 `ir.attachment` 的时机在 13.0；9→10 维持原状（`attachment=False` 默认）。
- `fields.Binary` 用法不变。

## 4. 红线

- `t-raw`/Jinja 邮件渲染 → 14→15；`subtype_xmlid` → 14→15；
- 控制器 `openerp.http`→`odoo.http` 改名属 **9→10**（本卷第 1 节已覆盖）；
- 工作流移除、Python 3 强制 → 10→11。
