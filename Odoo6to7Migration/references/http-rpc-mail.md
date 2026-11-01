# 6→7 HTTP / RPC / 邮件 / 二进制映射表（源码核对版）

> 来源：OpenERP 7.0 源码核对 —— 6→7 的 HTTP/邮件/二进制 API **基本不变**。
> 作用域：仅指出"无需改动"的边界 + 更晚版本的红线，避免误改。6/7 使用 `openerp` 包名。

## 1. HTTP / 控制器（不变）  — CONFIRMED

- `openerp.addons.web.http` 一脉的控制器、`@http.route` 装饰器、`request.registry` / `request.session` 在 6/7 行为一致。
- 无需改动自定义控制器；包名仍是 `openerp`（不是 `odoo`）。

## 2. 邮件 `message_post`（不变）  — CONFIRMED

- `message_post(body=..., subtype=..., message_type=...)` 在 6/7 行为一致。
- `mail.template` 渲染结构在 6→7 基本一致；大规模邮件/Jinja→QWeb 重写是 **14→15**，不在 6→7。

## 3. 二进制 / 资源路径（不变）  — CONFIRMED

- `Binary` 字段存储行为 6/7 一致（默认改存 `ir.attachment` 是 **13.0** `[verify]`）。
- 资源路径辅助函数 6/7 一致。

## 4. 红线（勿套用更晚版本）

- `message_post(body_is_html=...)` → 16→17；
- `subtype` → `subtype_xmlid` → 14→15；
- `get_resource_path` → `file_path` → 16→17；
- 资产进 manifest `assets` 键 → 14→15；
- `t-raw` 移除 / `ir.model*` 访问移除 → 14→15。

## 5. `[verify]`

- 邮件模板（`mail.template`）在 6→7 的 `body_html` / QWeb 渲染无变化；Jinja→QWeb 重写是 **14→15**。
