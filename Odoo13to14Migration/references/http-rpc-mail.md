# 13→14 HTTP / RPC / 邮件 / 二进制映射表（源码核对版）

> 来源：OCA 14.0 迁移指南核对 —— 13→14 的 HTTP/邮件/二进制 API **基本不变**。
> 作用域：仅指出"无需改动"的边界 + 更晚版本的红线，避免误改。

## 1. HTTP / 控制器（不变）  — CONFIRMED

- `@http.route` 装饰器、`http.Controller`、`request.env` 在 13/14 一致。
- `type='json'` 路由仍是 `json`（重命名为 `jsonrpc` 是 **18.1**，远晚于 14）。
- 无需改动自定义控制器。

## 2. 邮件 `message_post`（不变）  — CONFIRMED

- `message_post(body=..., subtype=..., message_type=...)` 在 13/14 行为一致。
- `body_is_html` 参数（HTML body 默认转义）是 **16→17** 引入，13→14 不涉及。
- `subtype` → `subtype_xmlid` 改名是 **14→15**，不在 13→14。

## 3. 二进制 / 资源路径（不变）  — CONFIRMED

- `get_resource_path` 在 13/14 仍使用（重命名为 `file_path` 是 **16→17**）。
- `Binary` 字段默认存储行为 13/14 一致（默认存 `ir.attachment` 自 **13.0** 起，12→13 已覆盖）。

## 4. 红线（勿套用更晚版本）

- `message_post(body_is_html=...)` → 16→17
- `subtype` → `subtype_xmlid` → 14→15
- `ir.model*` 访问移除 → 14→15（注意：13→14 仅限制 `ir.actions.*`，见 views-qweb.md）
- `t-raw` 移除 / 资产进 manifest → 14→15
- `get_resource_path` → `file_path` → 16→17

## 5. `[verify]`

- 邮件模板（`mail.template`）在 13→14 的 `body_html` / QWeb 渲染无变化；Jinja→QWeb 重写是 **14→15**。
