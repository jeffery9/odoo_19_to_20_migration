# 10→11 HTTP / RPC / 邮件 / 二进制 映射表（源码核对版）

> 来源：10.0/11.0 源码核对 + Odoo 官方 RPC 文档。
> 作用域：仅 10→11。本卷区间这些子系统**基本不变**。

## 1. HTTP / 控制器  — CONFIRMED（不变）

- 包已是 `odoo`：`from odoo import http`；`http.Controller`、`http.route()` 接口 10→11 无破坏性变更。
- XML-RPC / JSON-RPC 对外接口稳定。

## 2. 邮件 / 模板  — CONFIRMED（不变）

- `mail.template` 渲染仍用 QWeb；Jinja/Python-format 语法移除发生在 14→15，不属本卷。
- `message_post` / `message_subscribe` 接口稳定。

## 3. 二进制字段  — CONFIRMED（不变）

- `Binary` 默认存 `ir.attachment` 的时机在 13.0；10→11 维持原状（`attachment=False` 默认）。
- `fields.Binary` 用法不变。

## 4. pycompat 移除的连带影响  — CONFIRMED

- `openerp.tools.pycompat` 垫片在 11.0 移除，个别 `http`/`mail` 工具函数若内部用到 `izip/unichr/text_type` 等，会暴露为 Python 3 报错；按 `orm-api.md` 第 1 节语法清单处理调用方代码即可。

## 5. 红线

- `t-raw`/Jinja 邮件渲染 → 14→15；`subtype_xmlid` → 14→15；
- 控制器 `openerp.http`→`odoo.http` 改名属 9→10。
