# 11→12 HTTP / RPC / 邮件 / 二进制映射表（源码核对版）

> 来源：OCA 12.0 迁移指南核对 —— 11→12 的 HTTP/邮件/二进制 API **基本不变**。
> 作用域：仅指出"无需改动"的边界 + 更晚版本的红线，避免误改。

## 1. HTTP / 控制器（不变）  — CONFIRMED

- `@http.route` 装饰器、`http.Controller`、`request.env` 在 11/12 一致。
- `type='json'` 路由仍是 `json`（重命名为 `jsonrpc` 是 **18.1**，远晚于 12）。
- 无需改动自定义控制器。

## 2. 邮件 `message_post`（不变）  — CONFIRMED

- `message_post(body=..., subtype=..., message_type=...)` 在 11/12 行为一致。
- `body_is_html` 参数（HTML body 默认转义）是 **16→17** 引入，11→12 不涉及。
- `subtype` → `subtype_xmlid` 改名是 **14→15**，不在 11→12。

## 3. 二进制 / 资源路径（不变）  — CONFIRMED

- `get_resource_path` 在 11/12 仍使用（重命名为 `file_path` 是 **16→17**）。
- `Binary` 字段默认存储行为 11/12 一致（默认改存 `ir.attachment` 是 **13.0** `[verify]`）。

## 4. 红线（勿套用更晚版本）

- `message_post(body_is_html=...)` → 16→17
- `subtype` → `subtype_xmlid` → 14→15
- `get_resource_path` → `file_path` → 16→17
- `t-raw` 移除 / `ir.model*` 访问移除 → 14→15
- 资产进 `__manifest__.py` `assets` 键 → 14→15

## 5. `[verify]`

- 邮件模板（`mail.template`）在 11→12 的 `body_html` / QWeb 渲染无变化；Jinja→QWeb 重写是 **14→15**。
