# 7→8 HTTP / RPC / 邮件 / 二进制映射表（源码核对版）

> 来源：Odoo 8.0 Release Notes + 8.0 源码核对 —— 7→8 的 HTTP/邮件/二进制 API **基本不变**
> （8.0 的 new-API 主要是 ORM 层；控制器与邮件仍沿用旧范式）。作用域：仅指出
> "无需改动"的边界 + 更晚版本的红线，避免误改。

## 1. HTTP / 控制器（不变）  — CONFIRMED

- `@http.route` 装饰器、 `http.Controller`、 `request.env` 在 7/8 一致。
- 7.0 已是 `from openerp import http`（包名 `openerp`，**不是** `odoo`——`odoo` 改名是 9→10）。
- `type='json'` 路由仍是 `json`（重命名为 `jsonrpc` 是 **18.1**，远晚于 8）。
- 无需改动自定义控制器，但控制器内部若调用旧 `(cr, uid, ids, context)` 风格模型方法，
  应随 ORM 改写（见 `references/orm-api.md`）。

## 2. 邮件 `message_post`（不变）  — CONFIRMED

- `message_post(body=..., subtype=..., message_type=...)` 在 7/8 行为一致。
- `body_is_html` 参数（HTML body 默认转义）是 **16→17** 引入，7→8 不涉及。
- `subtype` → `subtype_xmlid` 改名是 **14→15**，不在 7→8。

## 3. 二进制 / 资源路径（不变）  — CONFIRMED

- `get_resource_path` 在 7/8 仍使用（重命名为 `file_path` 是 **16→17**）。
- `Binary` 字段默认存储行为 7/8 一致（默认改存 `ir.attachment` 是 **13.0** `[verify]`）。
- `fields.Binary` 在 new-API 中仍是 `fields.Binary(...)` 类属性写法（见 `references/models-mapping.md`）。

## 4. 红线（勿套用更晚版本）

- `message_post(body_is_html=...)` → 16→17
- `subtype` → `subtype_xmlid` → 14→15
- `get_resource_path` → `file_path` → 16→17
- `t-raw` 移除 / `ir.model*` 访问移除 → 14→15
- 资产进 `__manifest__.py` `assets` 键 → 14→15
- `type='json'` → `jsonrpc` → 18.1

## 5. `[verify]`

- 邮件模板（`mail.template`）在 7→8 的 `body_html` / QWeb 渲染无变化；Jinja→QWeb 重写是 **14→15**。
- 8.0 引入 `mail` 模块的部分 new-API 重构（如 `message_new` / `message_update` 的 recordset
  语义）属渐进改进，必要时对照 8.0 `mail` 模块源码确认。
